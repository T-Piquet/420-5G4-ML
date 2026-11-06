# Agent Guidance: Bibliotheque Library System

## Essential Information

### Build Process
```bash
mkdir build && cd build && cmake .. && make
./bibliotheque
```

### Data Format
- **Location**: `{data_dir}/books.txt`, `{data_dir}/users.txt` (relative to `-d|--data-dir`)
- **Format**: Pipe-separated values
  - `books.txt`: id|title|isbn|author|year
  - `users.txt`: id|name|email,borrowed_isbn1, borrowed_isbn2

### Application Usage
```bash
./bibliotheque                    # Uses default data directory
./bibliotheque -d ./my_data       # Custom data directory
```

### CMake Requirements
- Minimum C++17 standard
- Compiler warnings enabled
- Place `data/` directory in `-D` flag path

### Dev Container Notes
- X11 forwarding configured for GUI tools (if needed)
- Host networking enables external service connections
- Persistent volume mounts to `/data` inside container

### Source Structure
- `main.cpp`: Entry point with menu system
- `library.*`: Book/User data management
- `book.*`: Book CRUD operations
- `user.*`: User CRUD operations  
- `filemanager.*`: Data file I/O utilities
