
class Validation():
    def __init__(self):
        pass
    def validate(self, input_string)->int:
        try:
            compile(input_string, "bogusfile.py", "exec")
            return {"result": 1, "desc": "OK"}
        except Exception as e:
            return {"result": -2, "desc": str(e)}
