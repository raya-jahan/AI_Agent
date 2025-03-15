from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
import os
from tools.final_answer import FinalAnswerTool
from tools.price_comparison_tool import PriceComparisonTool

from Gradio_UI import GradioUI

import os
token = os.environ.get("HF_TOKEN")



# Calculator tool

@tool
def dynamic_calculator_tool(expression: str) -> float:
    """
    This tool is a dynamic calculator that safely evaluates an arithmetic expression.
    
    Args:
        expression: A string representing the arithmetic expression to evaluate.
                    For example: "2 + 3 * (4 - 1)"
                    
    Returns:
        The result of evaluating the expression, or an error message if the expression is invalid.
    """
    import ast
    import operator as op

    # Supported operators mapping
    allowed_operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.Mod: op.mod,
        ast.USub: op.neg,
    }

    def _eval_ast(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            left = _eval_ast(node.left)
            right = _eval_ast(node.right)
            if type(node.op) in allowed_operators:
                return allowed_operators[type(node.op)](left, right)
            else:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):  # - <operand>
            operand = _eval_ast(node.operand)
            if type(node.op) in allowed_operators:
                return allowed_operators[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        else:
            raise ValueError(f"Unsupported expression: {node}")

    try:
        # Parse the expression into an AST node
        node = ast.parse(expression, mode='eval').body
        result = _eval_ast(node)
        return result
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"



from tools.weather_tool import FreeWeatherTool  # Import the new weather tool




# Simple multiplication

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_calculator_tool(arg1:int, arg2:int)-> int: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """This tool is a calculator that multiplies two integers
    Args:
        arg1: the first argument takes one integer input
        arg2: the second argument takes another integer input
    """
    return arg1 * arg2












    

# Timezone

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()
weather_tool = FreeWeatherTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model_name = 'deepseek-ai/DeepSeek-R1'

model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    # model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
    model_id=model_id,
    custom_role_conversions=None,
)


# model = HfApiModel(
# max_tokens=2096,
# temperature=0.5,
# model_id='Qwen/Qwen2.5-Coder-32B-Instruct',# it is possible that this model may be overloaded
# custom_role_conversions=None,
# )



# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)


price_comparison_tool = PriceComparisonTool()
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, price_comparison_tool, weather_tool, dynamic_calculator_tool, my_calculator_tool, get_current_time_in_timezone], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)



port = int(os.environ.get('PORT', 7860))  # Use Render's dynamic port or 7860 for local
GradioUI(agent).launch(server_name="0.0.0.0", server_port=port)

# GradioUI(agent).launch()
