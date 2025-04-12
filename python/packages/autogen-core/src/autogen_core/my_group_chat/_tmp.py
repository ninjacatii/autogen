from datetime import datetime
from pathlib import Path

now: str = datetime.now().strftime("%Y%m%d%H%M%S")
output_path = Path(__file__).parent / "generated_images" / f"{now}.png"

path1 = Path(str(output_path))
print(str(path1))

