Of course. Here is a highly detailed description of the provided dashboard image, designed to allow for its recreation.

### **Overall Layout & Styling**

* **Theme:** A clean, modern, and professional theme with a light gray background (`#F7F8FA` or similar). The content is displayed in white cards with subtle box shadows.
* **Typography:** A sans-serif font like Inter, Roboto, or similar. Font weights vary between regular for body text/data and semi-bold/bold for titles and key figures.
* **Accent Color:** A primary blue (`#4A90E2` or similar) is used for selected items, positive values, and interactive elements. A red/pink (`#D0021B` or similar) is used for negative values, and a green (`#7ED321` or similar) is used for positive P&L values.
* **Structure:** The layout consists of a fixed left navigation sidebar, a top header bar, a main content area, and a bottom footer. The main content area is a grid that holds four main widgets.

---

### **1. Top Header Bar**

* **Position:** Fixed at the top of the page, spanning the full width of the main content area (not the sidebar).
* **Components (from left to right):**
  * **Page Title:** Large, bold text stating "KSIF Dashboard".
  * **Date Range Picker:**
    * **Appearance:** A button-like element with a calendar icon on the left. It displays the currently selected date range, e.g., "Aug 23, 2025 - Sep 22, 2025".
    * **Interaction:** Clicking this should open a calendar widget, allowing the user to select a start and end date to filter the dashboard data.
  * **Team Filter Dropdown:**
    * **Appearance:** A button-style dropdown showing "All Teams" with a downward-facing chevron icon.
    * **Interaction:** Clicking this reveals a list of available teams (e.g., "Team Alpha", "Team Beta", "All Teams"). Selecting an option filters the entire dashboard's data for that team.
  * **Currency Filter Dropdown:**
    * **Appearance:** A button-style dropdown showing "KRW" with a downward-facing chevron icon.
    * **Interaction:** Clicking this allows the user to change the currency for all monetary values on the dashboard (e.g., from KRW to USD).

### **2. Left Navigation Sidebar**

* **Position:** Fixed vertically on the far left of the screen.
* **Appearance:** A dark charcoal or off-black background (`#2C3E50` or similar).
* **Components (from top to bottom):**
  * **Logo/Header:** (Implied) Typically a company logo or name would be at the very top.
  * **Navigation Links:** A vertical list of links, each with an icon on the left and text on the right.
    * **Dashboard:** (Currently selected)
      * **Icon:** A 2x2 grid icon.
      * **Style:** The entire item has a solid blue background, and the icon and text are white. A blue vertical bar might also appear to its left.
    * **Positions:**
      * **Icon:** A pie chart or portfolio icon.
      * **Style:** White icon and text on the dark background.
    * **Transactions:**
      * **Icon:** A list or receipt icon.
      * **Style:** White icon and text.
    * **Reports:**
      * **Icon:** A bar chart or document icon.
      * **Style:** White icon and text.
    * **Teams:**
      * **Icon:** A group of people/users icon.
      * **Style:** White icon and text.
    * **Settings:**
      * **Icon:** A gear or cog icon.
      * **Style:** White icon and text.
  * **Interaction:**
    * **Hover:** Hovering over an unselected link should slightly lighten its background or underline the text.
    * **Click:** Clicking a link navigates to that page and applies the "selected" style to it.

### **3. Main Content Area**

This area is a grid containing four widget cards.

#### **3.1. Position Summary (Top Left)**

* **Appearance:** A large rectangular white card, taking up the vertical space of two standard cards.
* **Header:**
  * **Title:** "Position Summary" in bold text.
  * **Subtitle:** "Current open positions for All Teams" in a smaller, lighter font.
* **Content:** A data table.
  * **Columns:** Symbol, Quantity, Price, Market Value, P&L, P&L %. Column headers are bold.
  * **Rows:** Each row represents a stock holding.
    * **Samsung Electronics:** Quantity: 1,500, Price: ₩72,500, Market Value: ₩108,750,000, P&L: `₩12,500,000` (green text), P&L %: `13.00%` (green text).
    * **SK Hynix:** Quantity: 800, Price: ₩125,000, Market Value: ₩100,000,000, P&L: `-₩5,000,000` (red text), P&L %: `-4.76%` (red text).
    * **NAVER:** Quantity: 300, Price: ₩215,000, Market Value: ₩64,500,000, P&L: `₩7,500,000` (green text), P&L %: `13.16%` (green text).
    * **Kakao:** Quantity: 450, Price: ₩58,000, Market Value: ₩26,100,000, P&L: `-₩1,800,000` (red text), P&L %: `-6.45%` (red text).
  * **Table Footer:** A "Total" row with a top border separating it from the data. It sums the Market Value (`₩299,350,000`) and P&L (`₩13,200,000`, green text), and shows the weighted average P&L % (`4.61%`, green text).
* **Footer Section:** Two info boxes at the bottom of the card, side-by-side.
  * **Available Cash:** Title with the value `₩250,000,000` below it in large, bold text.
  * **Total Assets:** Title with the value `₩549,350,000` below it in large, bold text. (Note: Total Assets = Total Market Value + Available Cash).
* **Interaction:** Hovering over a table row could highlight it. Clicking a row might navigate to a detailed view for that symbol.

#### **3.2. Profit & Loss Report (Top Right)**

* **Appearance:** A standard-sized square-ish white card.
* **Header:**
  * **Title:** "Profit & Loss Report" in bold text.
  * **Subtitle:** "P&L analysis for All Teams" in a smaller, lighter font.
* **Controls:** A set of four toggle buttons: `Daily`, `Weekly`, `MTD`, `YTD`.
  * **Style:** `Daily` is selected with a solid blue background and white text. The others are unselected with a light gray border and blue text.
  * **Interaction:** Clicking a button updates the large P&L figure and the bar chart to reflect that time period.
* **Content:**
  * **Total P&L Figure:** A very large, green number showing the P&L for the selected period (`₩10,100,000`). Below it, a subtitle reads "Total P&L for the last 7 days".
  * **Bar Chart:**
    * **Y-axis:** Shows P&L values in millions of KRW (e.g., 400만, 300만).
    * **X-axis:** Shows dates for the last 7 days (e.g., 04/24, 04/25, ... 04/30).
    * **Bars:** Dark charcoal-colored vertical bars representing the P&L for each day. Bars can be positive (above the zero line) or negative (below the zero line).
  * **Interaction:** Hovering over a bar should display a tooltip with the exact date and P&L amount.

#### **3.3. Transaction History (Bottom Left)**

* **Appearance:** A standard-sized rectangular white card.
* **Header:**
  * **Title:** "Transaction History" in bold text.
  * **Subtitle:** "Recent trades for the selected period" in a smaller, lighter font.
  * **Controls (Right-aligned):** An "Export" button with a download icon, a search input field with a magnifying glass icon and placeholder "Search transactions...", and a "Type" dropdown filter.
* **Content:** A scrollable list/table of transactions, grouped by date.
  * **Date Group Header:** A header like "2023. 04. 30." separates transactions from different days.
  * **Transaction Item:** Each transaction shows:
    * **Left Side:** Transaction ID (e.g., TX123456) and a timestamp (e.g., 오전 09:30).
    * **Center:** Symbol (e.g., Samsung Electronics) and Type (e.g., a green "Buy" tag).
    * **Right Side:** Quantity, Price, and Total value (e.g., ₩95,000,000).
    * **Far Right:** The team associated with the trade (e.g., Team Alpha).
* **Interaction:**
  * The "Export" button would download the transaction history as a CSV or Excel file.
  * The search bar filters the list as the user types.
  * The "Type" dropdown filters by transaction type (e.g., Buy, Sell).
  * Clicking a transaction item could open a modal with more detailed information.

#### **3.4. Benchmark Comparison (Bottom Right)**

* **Appearance:** A standard-sized square-ish white card.
* **Header:**
  * **Title:** "Benchmark Comparison" in bold text.
  * **Subtitle:** "Portfolio performance % vs market indices" in a smaller, lighter font.
* **Controls / Legend:** A series of checkboxes at the top right act as both a legend and a filter.
  * **Items:** `Portfolio` (black square), `KOSPI` (purple), `KOSPI 200` (pink), `KOSDAQ` (blue), `S&P 500` (green), `DJIA` (orange), `USD/KRW` (red). Each has a colored key next to it.
  * **Interaction:** Clicking a checkbox toggles the visibility of the corresponding line on the chart below.
* **Content:** A multi-series line chart.
  * **Y-axis:** Percentage return, from -3% to 9%.
  * **X-axis:** Dates over the selected period (e.g., 04/01 to 04/30).
  * **Lines:** Multiple colored lines plotting the performance of each selected index. The "Portfolio" line is thicker and black, showing it as the primary series.
* **Interaction:** Hovering over the chart should display a vertical line and a tooltip that shows the exact percentage value for each visible series at that specific point in time.

### **4. Footer**

* **Position:** A thin bar at the very bottom of the page, below the main content area.
* **Components:**
  * **Left Side:** "Last updated: September 22nd, 2025 2:18 PM".
  * **Right Side:** Copyright and version information, e.g., "KSIF Dashboard v1.0 © 2025 Korea Securities Investment Fund".
