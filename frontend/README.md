# Lawyer Agent Frontend

A **React** application (Vite + TypeScript) that serves as the user interface for the Retail Strategy Agent. It features a chat interface and a dynamic visualization panel.

## Features

*   **Chat Interface**: Communicate with the AI agent. Includes message persistence and Markdown rendering.
*   **Data Visualization**: Integrated **Apache ECharts** rendering for rich, interactive charts.
    *   Supports Stacked Bars, Stacked Areas, Pie Charts, and Dual-Axis Mixed Charts.
    *   **Vivid Professional Palette**: 14-color Material Design palette for high-contrast visibility.
*   **Responsive Layout**:
    *   **Fixed Chat Panel**: The chat sidebar is fixed at `400px` to ensure the visualization area always has sufficient space.
    *   **Overflow Handling**: Chat bubbles handle wide content (tables, code) with internal scrolling.

## Key Components

### `ChatWindow.tsx`
The main container. Manages the state of the conversation and the active charts.
*   **State**: `activeECharts` holds the data for the current visualization.
*   **Layout**: Splits screen into Chat (Left, Fixed) and Charts (Right, Flex).

### `EChartsDisplay.tsx`
Renders the chart configurations received from the backend.
*   **Logic**: Detects `chart_type` ('bar', 'area', 'mixed') and configures ECharts options accordingly.
*   **Dual Axis**: Automatically configures secondary Y-axis for Mixed charts.

### `MessageList.tsx` & `MessageBubble.tsx`
Handles the display of chat history.
*   **Styling**: Uses distinct styles for User (Gold/Navy) and Agent (Navy/White) messages.
*   **Markdown**: Renders rich text, tables, and code blocks using `react-markdown`.

## Setup

1.  **Install Dependencies**:
    ```bash
    pnpm install
    ```
2.  **Run Development Server**:
    ```bash
    pnpm run dev
    ```
    Access at `http://localhost:5173`.
