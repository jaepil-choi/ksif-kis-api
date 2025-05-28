#!/usr/bin/env bash

# set -e: exit on command failure
# set -u: error on using undefined variables
# set -o pipefail: fail a pipeline if any command within it fails
set -euo pipefail

# ---------------------------------------------------------------------------
# CLI script that updates or reads a value from a JSON file using jq.
# By default, it targets /Applications/Cursor.app/Contents/Resources/app/product.json,
# but you can override that via --file=... or -f.
#
# Inspired by:
#   https://gist.github.com/joeblackwaslike/752b26ce92e3699084e1ecfc790f74b2
#
# Usage examples:
#   ./fix-product-json.sh
#   ./fix-product-json.sh -n
#   ./fix-product-json.sh '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion'
#   ./fix-product-json.sh '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion' 0.399.0
# ---------------------------------------------------------------------------

# Determine default target file based on OS
if [ "$(uname)" == "Darwin" ]; then
  TARGET_FILE="/Applications/Cursor.app/Contents/Resources/app/product.json"
elif [ "$(uname)" == "Linux" ]; then
  TARGET_FILE="/opt/Cursor/resources/app/product.json"
else
  echo "Unsupported OS. Please specify file path with --file or -f."
  exit 1
fi

APP_PATH=""
DRY_RUN=false

# Store the script name for usage
SCRIPT_NAME=$(basename "$0")

# Helper function for consistent logging
log_message() {
  local status="$1"
  local message="$2"
  echo "[${status}] ${message}"
}

usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [options] [command or json_path [args...]]

Options:
  --file, -f <path>   Override the default JSON file location
                      (default: ${TARGET_FILE})
  --dry-run, -n       Show what would be changed, but do not actually write
  --help, -h          Show this help message

Commands:
  update_gallery [target_file]     Apply only the extensionsGallery updates.
                                   If target_file is provided, it overrides --file.

JSON Operations:
  <json_path>                     Get the value at the JSON path
  <json_path> <new_value>         Update the value at the JSON path

If no arguments given, the script applies a predefined set of changes
to the default file. These include gallery and extension version updates.

Examples:
  # Perform the default updates (gallery, extensions) on the standard file
  ${SCRIPT_NAME}

  # Dry-run only (no changes written)
  ${SCRIPT_NAME} -n

  # Apply only gallery updates to the default file
  ${SCRIPT_NAME} update_gallery

  # Apply only gallery updates to a specific file using positional arg
  ${SCRIPT_NAME} update_gallery /custom/path/product.json

  # Print the current value from the default file
  ${SCRIPT_NAME} '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion'

  # Update that same key in the default file
  ${SCRIPT_NAME} '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion' 0.399.0
EOF
}

# Ensures the path starts with a leading dot if it doesn't already.
ensure_leading_dot() {
  local path="$1"
  if [ -z "$path" ]; then
    echo "$path"
  elif [[ "$path" == .* ]]; then
    echo "$path"
  else
    echo ".$path"
  fi
}

# Prints the current value of 'json_path' from 'file' using jq.
read_json_value() {
  local file="$1"
  local raw_path="$2"
  local path_to_use
  path_to_use="$(ensure_leading_dot "$raw_path")"

  if ! jq -e "$path_to_use" "$file" &>/dev/null; then
    log_message "NO_KEY" "${path_to_use}: key does not exist or cannot be retrieved."
    return 0
  fi

  local val
  val="$(jq -r "$path_to_use" "$file")"
  log_message "READ" "${path_to_use} => ${val}"
}

# Updates 'json_path' in 'file' to 'new_value' using jq.
# Uses a herestring to feed the new JSON into the original file.
update_json_value() {
  local file="$1"
  local raw_path="$2"
  local new_value="$3"
  local path_to_use
  path_to_use="$(ensure_leading_dot "$raw_path")"

  local key_missing=false
  if ! jq -e "$path_to_use" "$file" &>/dev/null; then
    key_missing=true
  fi

  local current_value
  current_value="$(jq -r "$path_to_use" "$file" 2>/dev/null || echo "")"

  if [ "$current_value" = "$new_value" ]; then
    log_message "NO_CHANGE" "${path_to_use}: Already => ${new_value}"
    return 0
  fi

  if [ "$DRY_RUN" = true ]; then
    if [ "$key_missing" = true ]; then
      log_message "WILL_CREATE" "${path_to_use}: Would create key and set to => ${new_value}"
    else
      log_message "WILL_UPDATE" "${path_to_use}: Would change from => ${current_value} to => ${new_value}"
    fi
    return 0
  fi

  # Generate new JSON content using jq (in a variable) so we can check if it failed
  local jq_out
  if ! jq_out="$(jq --arg val "$new_value" "$path_to_use |= \$val" "$file" 2>/dev/null)"; then
    log_message "ERROR" "jq failed trying to update ${path_to_use}"
    return 1
  fi

  if [ -z "$jq_out" ]; then
    log_message "ERROR" "jq produced no output for updating ${path_to_use}"
    return 1
  fi

  printf "%s\n" "$jq_out" >"$file"

  if [ "$key_missing" = true ]; then
    log_message "CREATED" "${path_to_use}: Set to => ${new_value}"
  else
    log_message "UPDATED" "${path_to_use}: Changed from => ${current_value} to => ${new_value}"
  fi
}

# Apply updates related to extensionsGallery
apply_gallery_updates() {
  local target_file="$1"
  log_message "INFO" "Applying extensionsGallery updates to => $target_file"
  
  # Switchover to MS VSCode Marketplace endpoints
  update_json_value "$target_file" .extensionsGallery.serviceUrl "https://marketplace.visualstudio.com/_apis/public/gallery"
  update_json_value "$target_file" .extensionsGallery.itemUrl "https://marketplace.visualstudio.com/items"
  update_json_value "$target_file" .extensionsGallery.resourceUrlTemplate "https://{publisher}.vscode-unpkg.net/{publisher}/{name}/{version}/{path}"
  update_json_value "$target_file" .extensionsGallery.controlUrl "https://main.vscode-cdn.net/extensions/marketplace.json"
  update_json_value "$target_file" .extensionsGallery.nlsBaseUrl "https://www.vscode-unpkg.net/_lp/"
  update_json_value "$target_file" .extensionsGallery.publisherUrl "https://marketplace.visualstudio.com/publishers"
}

# Apply updates related to extensionMaxVersions
apply_extension_version_updates() {
  local target_file="$1"
  log_message "INFO" "Applying extensionMaxVersions updates to => $target_file"
  
  # ms-python.python
  update_json_value "$target_file" '.extensionMaxVersions."ms-python.python".maxVersion' "2025.5.2025041801"
  
  # ms-python.debugpy
  update_json_value "$target_file" '.extensionMaxVersions."ms-python.debugpy".maxVersion' "2025.6.0"
  
  # ms-python.vscode-pylance
  update_json_value "$target_file" '.extensionMaxVersions."ms-python.vscode-pylance".maxVersion' "2025.4.100"
  
  # ms-vscode-remote.remote-containers
  update_json_value "$target_file" '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion' "0.399.0"
  
  # anysphere.pyright
  update_json_value "$target_file" '.extensionMaxVersions."anysphere.pyright".maxVersion' "0.0.0-0"
  
  # codeium.windsurfPyright
  update_json_value "$target_file" '.extensionMaxVersions."codeium.windsurfPyright".maxVersion' "0.0.0-0"
}

# Apply all predefined updates (default behavior)
apply_predefined_updates() {
  log_message "INFO" "Using file => $TARGET_FILE"
  log_message "INFO" "Applying all predefined updates..."

  apply_gallery_updates "$TARGET_FILE"
  apply_extension_version_updates "$TARGET_FILE"

  log_message "INFO" "Successfully completed all updates."
}

# Parse flags and any remaining positional arguments
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
  --file | -f)
    TARGET_FILE="$2"
    shift 2
    ;;
  --dry-run | -n)
    DRY_RUN=true
    shift
    ;;
  --help | -h)
    usage
    exit 0
    ;;
  *)
    # Treat anything else as a positional argument (json_path or new_value)
    POSITIONAL+=("$1")
    shift
    ;;
  esac
done

# Restore positional arguments
pos_count=0
if [ ${#POSITIONAL[@]:-0} -gt 0 ]; then
  set -- "${POSITIONAL[@]}"
  pos_count=$#
else
  # Clear arguments when POSITIONAL is empty
  set --
  pos_count=0
fi

# Ensure jq is installed
if ! command -v jq &>/dev/null; then
  log_message "ERROR" "'jq' is required but not installed."
  exit 1
fi

# Handle commands based on argument count
if [ "$pos_count" -gt 0 ]; then
  # First check if the first argument is a known command
  case "$1" in
    "update_gallery")
      if [ "$pos_count" -gt 2 ]; then
        log_message "ERROR" "update_gallery takes at most one argument (target_file)"
        usage
        exit 1
      fi
      # If a second argument is provided, use it as the target file
      if [ "$pos_count" -eq 2 ]; then
        TARGET_FILE="$2"
        log_message "INFO" "Overriding target file with argument => $TARGET_FILE"
      fi
      apply_gallery_updates "$TARGET_FILE"
      exit 0
      ;;

    *)
      # Handle as JSON operations
      if [ "$pos_count" -eq 1 ]; then
        # Treat as JSON path unless it's a command we missed?
        # "read" mode: show the existing JSON value
        read_json_value "$TARGET_FILE" "$1"
        exit 0
      elif [ "$pos_count" -eq 2 ]; then
        # "update" mode: update the JSON with the new value
        update_json_value "$TARGET_FILE" "$1" "$2"
        exit 0
      else
        # More than 2 positional args not matching a command is an error
        log_message "ERROR" "Invalid arguments or command."
        usage
        exit 1
      fi
      ;;
  esac
fi

# If no commands were handled above, apply the predefined updates
apply_predefined_updates
exit 0
