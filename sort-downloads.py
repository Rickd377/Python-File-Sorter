import os
from os.path import splitext, exists, join
from shutil import move
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source_dir = "C:/Users/rick-/Downloads"
dest_videos = "C:/Users/rick-/Documents/Downloaded Videos"
dest_audios = "C:/Users/rick-/Documents/Downloaded Audios"
dest_images = "C:/Users/rick-/Documents/Downloaded Images"
dest_documents = "C:/Users/rick-/Documents/Downloaded Documents"
dest_installers = "C:/Users/rick-/Documents/Downloaded Installers"
dest_zip = "C:/Users/rick-/Documents/Downloaded Zip"
dest_code = "C:/Users/rick-/Documents/Downloaded Code"

video_extensions = [".webm", ".mpg", ".mpeg", ".mp2", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]

audio_extensions = [".m4a", ".flac", ".mp3", ".wav", ".wma", ".aac"]

image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".jk2", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]

document_extensions = [".doc", ".docx", ".odt", ".txt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]

installers_extensions = [".exe", ".msi", ".dmg", ".deb", ".rpm"]

zip_extensions = [".zip"]

code_extensions = [".py", ".js", ".ts", ".java", ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".cs", ".rb", ".php", ".go", ".rs", ".swift", ".kt", ".kts", ".sh", ".bat", ".ps1", ".html", ".htm",
                   ".css", ".scss", ".sass", ".json", ".xml", ".yml", ".yaml", ".sql", ".pl", ".lua", ".r", ".m", ".vb", ".asm", ".md"]

def createFolders():
  for folder in [dest_videos, dest_audios, dest_images, dest_documents, dest_installers, dest_zip, dest_code]:
    os.makedirs(folder, exist_ok=True)

def make_unique_name(dest, name):
  filename, extension = splitext(name)
  counter = 1
  while exists(f"{dest}/{name}"):
    name = f"{filename}({str(counter)}){extension}"
    counter += 1
  return name

def move_file(dest, entry, name):
    try:
        target_path = join(dest, name)
        if exists(target_path):
            unique_name = make_unique_name(dest, name)
            target_path = join(dest, unique_name)
        move(entry.path, target_path)
        logging.info(f"Moved {name} to {target_path}")
    except Exception as e:
        logging.error(f"Error moving file {name} to {dest}: {e}")

class MoverHandler(FileSystemEventHandler):
  def process_file(self, entry):
     name = entry.name.lower()
     if any(name.endswith(ext) for ext in video_extensions):
        move_file(dest_videos, entry, entry.name)
     elif any(name.endswith(ext) for ext in audio_extensions):
        move_file(dest_audios, entry, entry.name)
     elif any(name.endswith(ext) for ext in image_extensions):
        move_file(dest_images, entry, entry.name)
     elif any(name.endswith(ext) for ext in document_extensions):
        move_file(dest_documents, entry, entry.name)
     elif any(name.endswith(ext) for ext in installers_extensions):
        move_file(dest_installers, entry, entry.name)
     elif any(name.endswith(ext) for ext in zip_extensions):
        move_file(dest_zip, entry, entry.name)
     elif any(name.endswith(ext) for ext in code_extensions):
        move_file(dest_code, entry, entry.name)

  def on_created(self, event):
     if event.is_directory:
        return
     time.sleep(1)
     try:
        with os.scandir(source_dir) as entries:
           for entry in entries:
              if entry.is_file():
                 self.process_file(entry)
     except Exception as e:
        logging.error(f"Error during new file scan: {e}")

if __name__ == "__main__":
   log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorter.log")
   logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(message)s',
      datefmt='%Y-%m-%d %H:%M:%S',
      handlers=[logging.FileHandler(log_path), logging.StreamHandler()]
   )

   createFolders()
   event_handler = MoverHandler()

   logging.info("Sorting existing files...")
   try:
      with os.scandir(source_dir) as entries:
         for entry in entries:
            if entry.is_file():
               event_handler.process_file(entry)
   except Exception as e:
      logging.error(f"Error scanning existing files: {e}")

   observer = Observer()
   observer.schedule(event_handler, source_dir, recursive=False)
   observer.start()
   logging.info("Observer started - watching Downloads for new files.")

   try:
      while True:
         time.sleep(1)
   except KeyboardInterrupt:
      observer.stop();
      logging.info("Observer stopped.")
   observer.join()