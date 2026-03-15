# CheatSheetHost

A lightweight, content-driven web server for hosting interactive cheatsheets and reference materials. Perfect for CTF (Capture The Flag) challenges, reverse engineering, and technical documentation.

## Features

- **Simple JSON-based Content**: Define cheatsheets using easy-to-edit JSON files
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Retro Terminal Theme**: Nostalgic green-on-black CRT monitor aesthetic
- **LAN Accessible**: Share cheatsheets across your local network
- **Multiple Section Types**: Tables, text blocks, code snippets, and ASCII tables
- **Hot Reload**: Refresh browser to see changes instantly
- **Threaded Server**: Handles multiple concurrent connections

## Quick Start

### Prerequisites

- Python 3.8 or higher

### Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/yourusername/CheatSheetHost.git
   cd CheatSheetHost
   ```

2. Run the server:
   ```bash
   python3 host_content_site.py
   ```

3. Open your browser to `http://127.0.0.1:8766`

The server will automatically create default files if they don't exist.

## Usage

### Accessing the Site

- **Local Access**: `http://127.0.0.1:8766`
- **Network Access**: `http://[your-local-ip]:8766` (displayed on startup)

### Navigation

- **Home Page**: Lists all available cheatsheets
- **Individual Pages**: Click any cheatsheet to view its content
- **Navigation Bar**: Quick links to all pages

### API Endpoint

- `GET /api/pages`: Returns JSON list of available page slugs

## Creating and Modifying Cheatsheets

Cheatsheets are stored as JSON files in the `pages/` directory. Each file defines a single page with the following structure:

```json
{
  "slug": "my-cheatsheet",
  "title": "My Custom Cheatsheet",
  "subtitle": "A brief description of this cheatsheet",
  "sections": [
    {
      "type": "table",
      "title": "Section Title",
      "items": [
        {"key": "Command", "value": "Description"},
        {"key": "Another", "value": "Command"}
      ]
    },
    {
      "type": "text",
      "title": "Notes",
      "text": "Some explanatory text here."
    },
    {
      "type": "code",
      "title": "Example Code",
      "language": "python",
      "code": "print('Hello, World!')"
    }
  ],
  "ascii": {
    "title": "ASCII Table",
    "blocks_across": 6,
    "min_width_px": 920
  }
}
```

### Section Types

- **table**: Key-value pairs displayed in a table format
- **text**: Plain text content (supports line breaks)
- **code**: Syntax-highlighted code blocks
- **ascii**: Special ASCII character table (optional)

### File Naming

- Files should be named descriptively (e.g., `gdb-cheatsheet.json`)
- The `slug` field determines the URL path (auto-generated from filename if omitted)
- JSON must be valid; invalid files are skipped with a warning

## Customization

### Styling

Edit `site_template.html` to modify the appearance:
- CSS variables in `:root` for colors and layout
- Responsive breakpoints for different screen sizes
- Terminal-style design elements

### Server Configuration

Command-line options:
```bash
python3 host_content_site.py --host 0.0.0.0 --port 8080
```

- `--host`: IP address to bind to (default: 0.0.0.0)
- `--port`: Port number (default: 8766)

## Project Structure

```
CheatSheetHost/
├── host_content_site.py    # Main server script
├── site_template.html      # HTML template and CSS
├── pages/                  # Cheatsheet JSON files
│   ├── ctf-cheatsheet.json
│   ├── gdb-cheatsheet.json
│   └── ...
└── README.md              # This file
```

## Included Cheatsheets

- **CTF Master Sheet**: Registers, syscalls, and common techniques
- **Bitwise / Crypto Pattern Recognition**: Reference for spotting bitwise operations, encoders, hashes, and crypto patterns
- **GDB/x64dbg**: Debugging commands and workflows
- **Ghidra**: Reverse engineering tool shortcuts
- **IDA Pro**: Disassembler hotkeys and features
- **Neovim**: Editor commands and configuration
- **Python for Reverse Engineering**: Practical Python reference for parsing, decoding, and rebuilding algorithms
- **WinDbg**: Windows debugging commands
- **x64 Assembly**: Instruction reference
- **x64 Shellcode Syscalls**: System call numbers
- **x86-32 Assembly**: 32-bit assembly reference

## Contributing

### Adding New Cheatsheets

1. Create a new JSON file in the `pages/` directory
2. Follow the JSON structure outlined above
3. Test by refreshing the browser
4. Submit a pull request

### Improving the Code

- The server is built with Python's `http.server` module
- Threading support for concurrent requests
- Minimal dependencies (only standard library)

### Reporting Issues

- Check server logs for JSON parsing errors
- Ensure JSON files are valid
- Test on different browsers/devices

## Development

### Running from Source

```bash
python3 host_content_site.py
```

### Testing Changes

- Edit JSON files and refresh browser
- Modify `site_template.html` for styling changes
- Restart server for Python code changes

## License

This project is open source. Feel free to use, modify, and distribute.

## Support

- For questions or issues, open a GitHub issue
- Contributions welcome via pull requests
- Star the repo if you find it useful!</content>