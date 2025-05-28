import sys
import re
import os.path

def get_args(command: str) -> str:
    '''Returns a string of arguments after the command

    Args:
        command (str): The command to get arguments from

    Return:
        str: The arguments of the command

    '''
    # Checks if command contains quotes
    if "'" in command:
        return command.split("'")[1:]
    elif '"' in command:
        return command.split('"')[1:]


    # Split command into words and join all parts after the first word (command name)
    # Example: for "echo hello world" returns "hello world"
    return ' '.join(command.split()[1:])

def find_path(command: str) -> str | None:
    '''Returns the path of the command or None if not found

    Args:
        command (str): The command to find the path of

        Returns:
            command (str): The path of the command if the command is a path

            full_path (str): The path of the command if the command is not a path

            None: If the command is not found
    '''

    #Checks if the path is the arg
    if os.path.exists(command):
        return command

    # Check if the command is in the PATH environment variable and returns a dictionary
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)

    # Traverses dictionary and grabs the path to listed arg if it exists else returns none
    for path_dir in path_dirs:
        full_path = os.path.join(path_dir, command)
        if os.path.exists(full_path):
            return full_path

    return None


def handle_quoted_args(command: str, is_double: bool) -> str:
    '''Handles quoted arguments of the command

    Args:
        command (str): The command to get arguments from
        is_double (bool): Whether the command is quoted with double quotes or not

    Return:

        command (str): The command with the quoted arguments rejoined without them
        or with them in the event that it is a path

        Example: for "echo 'hello world'" returns "echo hello world"
                "/documents/hello world" returns "/documents/hello world"

        result (str): The result of the command with spaces without the quotes

    '''
    args = get_args(command)
    if find_path(args) is not None:
        return command

    # Use the appropriate quote character
    quote = '"' if is_double else "'"

    # Split by quotes and rejoin without them
    parts = args.split(quote)

    if len(parts) >= 3:  # At least one quoted section exists
        # Reconstruct the command preserving spaces in quoted sections
        result = parts[0] # Command part
        for i in range(1, len(parts), 2):
            if i < len(parts) - 1:
                result += parts[i] + parts[i + 1] # Adds parts together
        return result

    return command


def main() -> None:
    '''Main function of the program. Contains shell functionality'''
    while True:
        # List of supported shell built-in commands
        built_ins = ["exit", "echo", "type", "pwd", "cd"]
        
        # Display shell prompt
        sys.stdout.write("$ ")
        command = input()

        # Use pattern matching to handle different commands
        match command:
            # Handle 'type' command - shows the type/location of a command
            case cmd if re.search(r"^type .*", cmd):
                arg = get_args(command)
                if arg in built_ins:
                    print(f"{arg} is a shell builtin")
                elif find_path(arg) != None:
                    # If the path exists, show its location
                    print(f"{arg} is {find_path(arg)}")
                else:
                    print(f"{arg}: not found")

            # Handle echo command - prints its arguments
            case cmd if re.search(r"^echo .*", cmd):
                processed_cmd = cmd
                if "'" in cmd:
                    processed_cmd = handle_quoted_args(cmd, False)
                elif '"' in cmd:
                    processed_cmd = handle_quoted_args(cmd, True)
                print(get_args(processed_cmd))


            case cmd if re.search(r"^cd .*", cmd):
                # Use pattern matching to handle different cases for cd command
                path = get_args(command)
                match path:
                    # Handles home directory
                    case p if p.startswith("~"):
                        try:
                            os.chdir(os.path.expanduser("~"))
                        except FileNotFoundError:
                            print(f"cd: {path}: No such file or directory")
                    # Error message for invalid directory
                    case invalid if find_path(path) is None:
                        print(f"cd: {path}: No such file or directory")
                    # Change the directory to the argument if it exists
                    case _:
                        os.chdir(path)

            # handles pwd command and prints current-working-directory or cwd
            case "pwd":
                print(os.getcwd())

            # Handles escape sequence
            case "exit 0":
                break
            
            # Default case - command not recognized or runs command from the user's library
            case _:
                if find_path(command.split()[0]) != None:
                    # If the command is found, run it
                    os.system(command)
                else:
                    print(f"{command}: command not found")

if __name__ == "__main__":
    '''Main entry point of the program'''
    # Start the shell when the script is run directly
    main()