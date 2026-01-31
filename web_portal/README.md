# Web Portal for Generic Simulator

A modern, responsive web interface for the Generic Simulator. This portal provides a user-friendly interface to manage configurations, view simulation results, and visualize process flows.

## Features

### 🏠 Home Dashboard
- System status overview
- Quick access to all features
- Configuration and simulation statistics

### 📋 Configuration Management
- View all available configurations
- Create new configurations
- Edit existing configurations with JSON editor
- Real-time validation before saving
- Device parameter management

### 📊 Simulation Dashboard
- Detailed simulation metrics
- Staff utilization analytics
- Device activity tracking
- Event timeline visualization
- Recent events table

### 🔄 Process Flow Visualizer
- Interactive flow diagrams
- Visual representation of device dependencies
- Click devices to view details
- Entry device highlighting
- Connection arrows showing workflow

## Prerequisites

- Azure Functions API running (see `api_function_app/README.md`)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Python HTTP server or any static file server

## Quick Start

### Option 1: Using Python HTTP Server

```bash
cd web_portal
python3 -m http.server 8000
```

Then open your browser to: `http://localhost:8000`

### Option 2: Using Node.js HTTP Server

```bash
cd web_portal
npx http-server -p 8000
```

Then open your browser to: `http://localhost:8000`

### Option 3: Using VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click `index.html` and select "Open with Live Server"

## Configuration

The web portal connects to the Azure Functions API. By default, it expects the API to be running at:

```
http://localhost:7071/api
```

To change the API endpoint, edit `js/api.js`:

```javascript
class SimulatorAPI {
    constructor(baseUrl = 'http://localhost:7071/api') {
        this.baseUrl = baseUrl;
    }
    // ...
}
```

For production deployments, update the `baseUrl` to your deployed Azure Functions URL:

```javascript
constructor(baseUrl = 'https://your-function-app.azurewebsites.net/api') {
```

## Usage

### Viewing Configurations

1. Navigate to **Configurations** page
2. Browse available configurations
3. Click **View Details** on any configuration
4. See devices, timing parameters, and dependencies

### Editing Configurations

1. Click **View Details** on a configuration
2. Click **Edit** button
3. Modify configuration in JSON editor
4. Click **Validate** to check for errors
5. Click **Save** to save changes

### Creating New Configurations

1. Go to **Configurations** page
2. Click **+ New Configuration**
3. Fill in configuration details
4. Edit the JSON structure
5. Click **Validate** then **Save**

### Viewing Simulation Results

1. Run a simulation using the CLI:
   ```bash
   python main.py --config configs/platelet_pooling.json --output outputs/results.json
   ```
2. Navigate to **Dashboard** page
3. Click **🔄 Refresh** to load latest results
4. View metrics, staff utilization, and event timeline

### Visualizing Process Flow

1. Navigate to **Process Flow** page
2. Select a configuration from dropdown
3. View interactive flow diagram
4. Click on devices to see details

## File Structure

```
web_portal/
├── index.html              # Home page
├── css/
│   └── styles.css         # Global styles
├── js/
│   ├── api.js             # API client
│   ├── home.js            # Home page logic
│   ├── configurations.js  # Configuration management
│   ├── dashboard.js       # Dashboard logic
│   └── visualizer.js      # Flow visualization
└── pages/
    ├── configurations.html # Configuration page
    ├── dashboard.html      # Dashboard page
    └── visualizer.html     # Visualizer page
```

## Features Overview

### Home Page (`index.html`)
- Welcome message
- Feature cards with quick access
- Quick start guide
- System status display

### Configurations Page (`pages/configurations.html`)
- List all configurations
- View configuration details
- Edit configurations with JSON editor
- Create new configurations
- Validation before saving

### Dashboard Page (`pages/dashboard.html`)
- Simulation metadata
- Event count and timing
- Staff utilization metrics
- Device activity analysis
- Event timeline
- Recent events table

### Visualizer Page (`pages/visualizer.html`)
- Canvas-based flow diagram
- Device nodes with connections
- Interactive device selection
- Device detail panel
- Entry device highlighting

## API Integration

The web portal uses the following API endpoints:

- `GET /api/config?list=true` - List all configurations
- `GET /api/config?file={filename}` - Get specific configuration
- `GET /api/config` - Get latest configuration
- `POST /api/config` - Save configuration
- `POST /api/config?validate_only=true` - Validate configuration
- `GET /api/events` - Get latest simulation events
- `GET /api/events?file={filename}` - Get specific simulation results

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### API Connection Issues

**Problem**: "Failed to load configurations" or "API Offline"

**Solution**:
1. Make sure the Azure Functions API is running:
   ```bash
   cd api_function_app
   func start
   ```
2. Check the API URL in `js/api.js`
3. Check browser console for CORS errors
4. If using Azure Functions, enable CORS in `local.settings.json`

### No Data Showing

**Problem**: Dashboard shows "No simulations yet"

**Solution**:
1. Run a simulation first:
   ```bash
   python main.py --config configs/platelet_pooling.json --output outputs/results.json
   ```
2. Click the refresh button
3. Check that output files exist in `outputs/` directory

### Configuration Validation Fails

**Problem**: "Validation failed" when saving configuration

**Solution**:
1. Check JSON syntax is correct
2. Ensure all required fields are present (devices, id, type)
3. Verify timing parameters (max >= min)
4. Check device output references exist
5. Review error message for specific issue

## Deployment

### Static Hosting (Recommended)

Deploy to any static hosting service:

**GitHub Pages:**
1. Push web_portal files to repository
2. Enable GitHub Pages in repository settings
3. Update API URL to production endpoint

**Netlify:**
```bash
cd web_portal
netlify deploy --prod
```

**Vercel:**
```bash
cd web_portal
vercel --prod
```

**Azure Storage Static Website:**
1. Create Azure Storage account
2. Enable static website hosting
3. Upload web_portal files
4. Update API URL to production endpoint

### CORS Configuration

For production, configure CORS in your Azure Function App:

```bash
az functionapp cors add \
  --name your-function-app \
  --resource-group your-resource-group \
  --allowed-origins https://your-web-portal-domain.com
```

## Customization

### Changing Colors

Edit `css/styles.css` to change the color scheme:

```css
:root {
    --primary-color: #2563eb;    /* Main brand color */
    --secondary-color: #7c3aed;  /* Secondary brand color */
    --success-color: #10b981;    /* Success indicators */
    --danger-color: #ef4444;     /* Error/danger indicators */
    /* ... */
}
```

### Adding New Pages

1. Create new HTML file in `pages/`
2. Create corresponding JS file in `js/`
3. Add navigation link to all pages
4. Follow existing structure and styling

## Security Considerations

- **API Keys**: Never commit API keys to the repository
- **CORS**: Configure appropriate CORS settings for production
- **HTTPS**: Always use HTTPS in production
- **Input Validation**: API validates all inputs server-side
- **XSS Protection**: Use textContent instead of innerHTML for user data

## Future Enhancements

- [ ] Real-time simulation monitoring via WebSockets
- [ ] Drag-and-drop configuration builder
- [ ] Advanced charts and graphs (Chart.js integration)
- [ ] Export results to PDF/CSV
- [ ] User authentication and authorization
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Mobile app version

## Support

For issues or questions:
- Check API documentation in `api_function_app/README.md`
- Review browser console for errors
- Ensure API is running and accessible
- Check CORS settings if seeing connection errors

## License

[Specify your license here]

---

**Version**: 1.0  
**Last Updated**: 2026-01-31
