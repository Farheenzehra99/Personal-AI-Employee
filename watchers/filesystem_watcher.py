from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import time

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        print("New file detected:", source)
        dest = self.needs_action / f'FILE_{source.name}'
        shutil.copy2(source, dest)
        self.create_metadata(source, dest)

    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
---

New file dropped for processing.
''')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Filesystem Watcher for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for cron)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    inbox_path = vault_path / 'Inbox'
    
    # Ensure inbox exists
    inbox_path.mkdir(parents=True, exist_ok=True)
    
    event_handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, path=inbox_path, recursive=False)
    observer.start()
    print(f"Watcher started... Monitoring {inbox_path}")
    
    if args.once:
        # Run once mode - wait 2 seconds for any pending events then exit
        import time
        time.sleep(2)
        observer.stop()
        observer.join()
        print("Watcher completed single check")
    else:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
