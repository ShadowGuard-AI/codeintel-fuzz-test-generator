#!/usr/bin/env python3
import argparse
import ast
import logging
import os
import sys
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default values
DEFAULT_NUM_TESTS = 10
DEFAULT_STRING_LENGTH = 10
DEFAULT_INT_RANGE = (-100, 100)


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Generates basic fuzz tests based on code structure and function signatures."
    )

    parser.add_argument(
        "module_path",
        help="Path to the Python module containing the functions to fuzz test."
    )

    parser.add_argument(
        "--num_tests",
        type=int,
        default=DEFAULT_NUM_TESTS,
        help="Number of fuzz tests to generate per function. Defaults to 10."
    )

    parser.add_argument(
        "--string_length",
        type=int,
        default=DEFAULT_STRING_LENGTH,
        help="Length of random strings used in fuzzing. Defaults to 10."
    )

    parser.add_argument(
        "--int_min",
        type=int,
        default=DEFAULT_INT_RANGE[0],
        help="Minimum integer value for fuzzing. Defaults to -100."
    )

    parser.add_argument(
        "--int_max",
        type=int,
        default=DEFAULT_INT_RANGE[1],
        help="Maximum integer value for fuzzing. Defaults to 100."
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="Optional file to save the generated tests to. If not provided, tests will be printed to stdout."
    )
    return parser


def generate_fuzz_input(param_type, string_length=DEFAULT_STRING_LENGTH, int_range=DEFAULT_INT_RANGE):
    """
    Generates a random input based on the specified parameter type.
    Supports int, float, str, bool, and None. Other types return None.
    """
    try:
        if param_type is int:
            return random.randint(int_range[0], int_range[1])
        elif param_type is float:
            return random.uniform(int_range[0], int_range[1])
        elif param_type is str:
            return ''.join(random.choice(string.ascii_letters) for _ in range(string_length))
        elif param_type is bool:
            return random.choice([True, False])
        elif param_type is type(None):
            return None
        else:
            logging.warning(f"Unsupported parameter type: {param_type}. Returning None.")
            return None  # Unsupported type
    except Exception as e:
        logging.error(f"Error generating fuzz input for type {param_type}: {e}")
        return None


def _annotation_type(node):
    """Maps an annotation node, rendered from source, to a type."""
    if node is None:
        return str
    try:
        name = ast.unparse(node).strip()
    except Exception:
        return str
    return {"int": int, "float": float, "str": str, "bool": bool}.get(name, str)


def generate_fuzz_tests(module_path, num_tests=DEFAULT_NUM_TESTS, string_length=DEFAULT_STRING_LENGTH, int_range=DEFAULT_INT_RANGE):
    """
    Generates fuzz tests for functions in a given module.

    The target module is read and parsed with ast only. It is never
    imported or executed, so its top level code does not run.

    Returns a list of test case strings, or None when the target
    cannot be read or parsed.
    """
    try:
        with open(module_path, "r") as f:
            source = f.read()
    except OSError as e:
        logging.error(f"Failed to read module {module_path}: {e}")
        return None
    try:
        tree = ast.parse(source, filename=module_path)
    except SyntaxError as e:
        logging.error(f"Failed to parse module {module_path}: {e}")
        return None

    # Defaults are rendered from the source where they are written
    # with ast.unparse; generation itself fills every parameter with
    # a fuzz value, matching the previous generator's output shape.
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    test_cases = []
    for func in functions:
        try:
            positional = list(func.args.posonlyargs) + list(func.args.args)
            defaults = [None] * (len(positional) - len(func.args.defaults)) + list(func.args.defaults)
            param_specs = []
            for arg_node, default_node in zip(positional, defaults):
                default_text = ast.unparse(default_node) if default_node is not None else None
                param_specs.append((arg_node.arg, _annotation_type(arg_node.annotation), "pos", default_text))
            if func.args.vararg is not None:
                param_specs.append((func.args.vararg.arg, int, "varpos", None))
            for arg_node, default_node in zip(func.args.kwonlyargs, func.args.kw_defaults):
                default_text = ast.unparse(default_node) if default_node is not None else None
                param_specs.append((arg_node.arg, _annotation_type(arg_node.annotation), "kwonly", default_text))
            if func.args.kwarg is not None:
                param_specs.append((func.args.kwarg.arg, int, "varkw", None))

            for i in range(num_tests):
                args = []
                kwargs = {}
                for param_name, param_type, kind, _default_text in param_specs:
                    if kind == "varpos":
                        args.extend([generate_fuzz_input(int, string_length, int_range) for _ in range(random.randint(0, 3))])
                        continue
                    if kind == "varkw":
                        kwargs.update({
                            ''.join(random.choice(string.ascii_lowercase) for _ in range(5)): generate_fuzz_input(int, string_length, int_range)
                            for _ in range(random.randint(0, 3))
                        })
                        continue
                    arg = generate_fuzz_input(param_type, string_length, int_range)
                    if kind == "kwonly":
                        kwargs[param_name] = arg
                    else:
                        args.append(arg)

                args_str = ", ".join(repr(arg) for arg in args)
                kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
                if args_str and kwargs_str:
                    call_str = f"{func.name}({args_str}, {kwargs_str})"
                elif args_str:
                    call_str = f"{func.name}({args_str})"
                elif kwargs_str:
                    call_str = f"{func.name}({kwargs_str})"
                else:
                    call_str = f"{func.name}()"

                test_case = f"# Test case {i+1} for function: {func.name}\n"
                test_case += f"# Call: {call_str}\n"
                test_case += f"try:\n"
                test_case += f"    result = {call_str}\n"
                test_case += f"    print(f'Function {func.name} executed successfully. Result: {{result}}')\n"
                test_case += f"except Exception as e:\n"
                test_case += f"    print(f'Function {func.name} raised an exception: {{e}}')\n\n"
                test_cases.append(test_case)
        except Exception as e:
            logging.error(f"Error generating test case for function {func.name}: {e}")

    return test_cases


def main():
    """
    Main function to parse arguments, generate fuzz tests, and print/save them.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Input validation
    if not os.path.exists(args.module_path):
        logging.error(f"Module path does not exist: {args.module_path}")
        sys.exit(1)

    if args.num_tests <= 0:
        logging.error("Number of tests must be greater than zero.")
        sys.exit(1)

    if args.string_length <= 0:
        logging.error("String length must be greater than zero.")
        sys.exit(1)

    if args.int_min > args.int_max:
        logging.error("Integer minimum must be less than or equal to integer maximum.")
        sys.exit(1)


    tests = generate_fuzz_tests(
        args.module_path,
        args.num_tests,
        args.string_length,
        (args.int_min, args.int_max)
    )

    if tests is None:
        print("Failed to generate fuzz tests: the target module could not be read or parsed.")
        sys.exit(1)

    if not tests:
        print("Failed to generate fuzz tests: no functions defined in the target module.")
        sys.exit(1)

    if args.output_file:
        try:
            with open(args.output_file, "w") as f:
                for test_case in tests:
                    f.write(test_case)
            logging.info(f"Fuzz tests saved to: {args.output_file}")
        except Exception as e:
            logging.error(f"Error writing to output file: {e}")
            sys.exit(1)
    else:
        for test_case in tests:
            print(test_case)

if __name__ == "__main__":
    main()