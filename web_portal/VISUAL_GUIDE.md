# Web Portal Visual Guide

This document provides a visual overview of the Generic Simulator Web Portal.

## Home Page (index.html)

The landing page features:

```
┌────────────────────────────────────────────────────────────────┐
│ ⚙️ Generic Simulator Portal                                    │
│                                                                  │
│ [Home] [Configurations] [Dashboard] [Process Flow]             │
└────────────────────────────────────────────────────────────────┘

        Welcome to the Generic Simulator Portal
     Model, simulate, and analyze complex process workflows

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   📋                │  │   📊                │  │   🔄                │
│ Configuration       │  │ Simulation          │  │ Process             │
│ Management          │  │ Dashboard           │  │ Visualization       │
│                     │  │                     │  │                     │
│ Create, edit, and   │  │ View detailed       │  │ Interactive flow    │
│ manage process      │  │ metrics, event      │  │ diagrams showing    │
│ configurations      │  │ timelines, and      │  │ device dependencies │
│                     │  │ performance         │  │ and workflows       │
│ [View Configs] ───→ │  │ [Open Dashboard] ─→ │  │ [View Flow] ─────→  │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘

                          Quick Start
        
        1. Select Configuration → 2. Edit Parameters → 3. View Results
        
                        System Status
        ┌──────────────────────────────────────────────────────┐
        │ API Status: ✓ Online                                │
        │ Configurations: 4                                    │
        │ Last Simulation: 2026-01-31 04:55:20               │
        └──────────────────────────────────────────────────────┘
```

## Configurations Page

Shows all available configurations with details:

```
┌────────────────────────────────────────────────────────────────┐
│ Process Configurations                      [+ New Config]     │
└────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ Platelet Pooling     │  │ Manufacturing        │  │ Platelet Pooling     │
│ Process              │  │ Assembly Line        │  │ with Staff           │
│                      │  │                      │  │                      │
│ Lifeblood platelet   │  │ Multi-stage assembly │  │ With staff           │
│ pooling simulation   │  │ process              │  │ utilization          │
│                      │  │                      │  │                      │
│ 8 devices  v1.0      │  │ 12 devices  v1.0     │  │ 8 devices  v1.0      │
│                      │  │                      │  │                      │
│ [View Details] ────→ │  │ [View Details] ────→ │  │ [View Details] ────→ │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

                    Configuration Details
┌────────────────────────────────────────────────────────────────┐
│ Platelet Pooling Process                    [Edit] [Close]    │
├────────────────────────────────────────────────────────────────┤
│ Description: Lifeblood platelet pooling simulation             │
│ Version: 1.0                                                    │
│                                                                 │
│ Devices:                                                        │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Device ID    │ Type        │ Exec Time  │ Fail % │ Out   │  │
│ ├──────────────────────────────────────────────────────────┤  │
│ │ collection   │ collection  │ 15s - 30s  │ 1.0%   │ qc_1  │  │
│ │ quality_ch_1 │ quality     │ 3s - 5s    │ 5.0%   │ store │  │
│ │ storage_temp │ storage     │ 60s - 120s │ 2.0%   │ pool  │  │
│ │ ...          │ ...         │ ...        │ ...    │ ...   │  │
│ └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘

                    Configuration Editor
┌────────────────────────────────────────────────────────────────┐
│ Configuration Editor         [Save] [Validate] [Cancel]       │
├────────────────────────────────────────────────────────────────┤
│ Configuration Name: [Platelet Pooling Process____________]     │
│ Description: [Lifeblood platelet pooling simulation_____]      │
│ Version: [1.0___]                                              │
│                                                                 │
│ Configuration JSON:                                             │
│ ┌────────────────────────────────────────────────────────┐    │
│ │ {                                                       │    │
│ │   "name": "Platelet Pooling Process",                  │    │
│ │   "description": "Lifeblood platelet pooling...",      │    │
│ │   "version": "1.0",                                    │    │
│ │   "devices": [                                         │    │
│ │     {                                                  │    │
│ │       "id": "collection",                              │    │
│ │       "type": "collection_station",                    │    │
│ │       ...                                              │    │
│ └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

## Dashboard Page

Displays simulation metrics and analytics:

```
┌────────────────────────────────────────────────────────────────┐
│ Simulation Dashboard                         [🔄 Refresh]      │
└────────────────────────────────────────────────────────────────┘

                      Simulation Metrics
┌────────────────────────────────────────────────────────────────┐
│ Total Events: 42                    Simulation Time: 156.3s    │
│ Generated At: 2026-01-31 04:55:20   Total Devices: 8           │
└────────────────────────────────────────────────────────────────┘

                    Staff Utilization
┌────────────────────────────────────────────────────────────────┐
│ Staff Type   │ Count │ Utilization │ Busy Time │ Allocations  │
├──────────────────────────────────────────────────────────────┤
│ technician   │   3   │   9.6%      │  56.9s    │     4        │
│ nurse        │   2   │   6.2%      │  32.8s    │     1        │
│ quality_spec │   2   │   3.1%      │  16.5s    │     2        │
└────────────────────────────────────────────────────────────────┘

                     Device Activity
┌────────────────────────────────────────────────────────────────┐
│ Device       │ Status    │ Exec Time │ Events                 │
├──────────────────────────────────────────────────────────────┤
│ collection   │ Complete  │  17.2s    │ Starts: 1, Comp: 1    │
│ quality_ch_1 │ Complete  │   4.1s    │ Starts: 1, Comp: 1    │
│ storage_temp │ Complete  │  89.3s    │ Starts: 1, Comp: 1    │
│ ...          │ ...       │  ...      │ ...                    │
└────────────────────────────────────────────────────────────────┘

                      Event Timeline
┌────────────────────────────────────────────────────────────────┐
│    0.00s | SYSTEM               | simulation_start            │
│    0.00s | collection           | staff_allocated             │
│    0.00s | collection           | start                       │
│    2.00s | collection           | execution_start             │
│   19.16s | collection           | execution_complete          │
│   19.16s | collection           | exit_start                  │
│   20.16s | collection           | complete                    │
│   20.16s | quality_check_1      | start                       │
│    ...                                                         │
└────────────────────────────────────────────────────────────────┘
```

## Process Flow Visualizer

Interactive flow diagram with device connections:

```
┌────────────────────────────────────────────────────────────────┐
│ Process Flow Visualizer         [Select Config ▼] [🔄 Refresh]│
└────────────────────────────────────────────────────────────────┘

                      Process Flow
┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│    ┌──────────┐         ┌──────────┐         ┌──────────┐     │
│    │Collection│────────→│Quality   │────────→│ Storage  │     │
│    │          │         │ Check 1  │         │   Temp   │     │
│    └──────────┘         └──────────┘         └──────────┘     │
│                                                     │           │
│                                                     ↓           │
│                                                ┌──────────┐     │
│                                                │ Pooling  │     │
│                                                └──────────┘     │
│                                                  │      │       │
│                                        ┌─────────┘      └────┐  │
│                                        ↓                     ↓  │
│                                  ┌──────────┐         ┌────────┐│
│                                  │Quality   │         │Labeling││
│                                  │ Check 2  │         │        ││
│                                  └──────────┘         └────────┘│
│                                        │                     │  │
│                                        └──────────┬──────────┘  │
│                                                   ↓             │
│                                              ┌──────────┐       │
│                                              │Packaging │       │
│                                              └──────────┘       │
│                                                   │             │
│                                                   ↓             │
│                                              ┌──────────┐       │
│                                              │  Final   │       │
│                                              │ Storage  │       │
│                                              └──────────┘       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

                      Device Details
┌────────────────────────────────────────────────────────────────┐
│ Device ID: collection                                           │
│ Type: collection_station                                        │
│ Timing: Start: 2.0s, Execution: 15.0s - 30.0s, Exit: 1.0s     │
│ Failure Probability: 1.0%                                       │
│ Outputs (Downstream): quality_check_1                           │
└────────────────────────────────────────────────────────────────┘

                         Legend
┌────────────────────────────────────────────────────────────────┐
│ ● Device Node    ─── Device Connection    ● Entry Device      │
└────────────────────────────────────────────────────────────────┘
```

## Features Demonstrated

### 1. Home Page
- Clean, modern design with gradient header
- Feature cards for quick navigation
- System status display
- Quick start guide

### 2. Configurations
- Grid layout of all configurations
- Detailed view with device table
- JSON editor for advanced editing
- Real-time validation

### 3. Dashboard
- Comprehensive simulation metrics
- Staff utilization breakdown
- Device activity tracking
- Event timeline with timestamps
- Color-coded status badges

### 4. Visualizer
- Canvas-based flow diagram
- Interactive device nodes
- Clickable devices for details
- Connection arrows showing workflow
- Entry device highlighting

## Responsive Design

All pages are fully responsive and work on:
- Desktop (1920x1080 and above)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667 and larger)

## Color Scheme

- Primary: Blue (#2563eb)
- Secondary: Purple (#7c3aed)
- Success: Green (#10b981)
- Danger: Red (#ef4444)
- Background: Light gray (#f9fafb)
- Text: Dark gray (#111827)

## Accessibility

- Semantic HTML5 elements
- ARIA labels where appropriate
- Keyboard navigation support
- High contrast text
- Readable font sizes
- Focus indicators

---

**Note**: This is a static visual representation. The actual portal is interactive and connects to the Azure Functions API for live data.
