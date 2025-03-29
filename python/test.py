from pydantic import BaseModel
import jsonref
from typing import Dict, Any

class InnerModel(BaseModel):
    value: int

class OuterModel(BaseModel):
    inner: InnerModel

# 创建 OuterModel 实例并获取 JSON 模式
outer = OuterModel(inner=InnerModel(value=42))
model_schema = outer.model_json_schema()

print("")
print(model_schema)

if "$defs" in model_schema:
    model_schema = jsonref.replace_refs(obj=model_schema, proxies=False)
    del model_schema["$defs"]

print("")
print(model_schema)