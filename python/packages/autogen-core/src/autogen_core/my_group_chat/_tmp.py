from datetime import datetime
import os
from pathlib import Path

now: str = datetime.now().strftime("%Y%m%d%H%M%S")
output_path = Path(__file__).parent / "generated_images" / f"{now}.png"

path1 = Path(str(output_path))

flag: bool = os.environ["IMAGE_GEN_FLAG"] == "DEV"

print(flag)

