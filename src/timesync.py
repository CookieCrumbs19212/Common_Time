import sys
from typing import Tuple
from datetime import datetime

from timeframe import TimeFrame
from utils import clear_screen, format_time, format_utc_offset, \
    is_valid_datetime, is_valid_offset, construct_timeframe_table


# Datetime format.
DATETIME_FORMAT = "%d-%m-%y %H:%M"

# Dict to store the timeframes. Timeframes are stored as {timeframe_id: TimeFrame_object}
TIMEFRAMES = {}

# Help description.
HELP_DESCRIPTION = """\
CLI tool to find the longest shared timeframe among several timeframes across different timezones.

Commands:
    add <timeframe-id> <utc-offset> <start-time> <end-time>
            - add a timeframe.
    remove <timeframe-id>
            - remove a timeframe.

    see documentation for further usage details.

    reset   - clear all timeframes.

    run     - find the shared timeframe.
    ls      - list all the timeframes.
    vis     - visualize the timeframes.
            
    clear   - clears the screen.
    help    - view the help description.
    exit    - exit TimeSync.
"""


def add_timeframe(timeframe_id: str, utc_offset: str, start_time: datetime, end_time: datetime) -> None:
    """ Add a new timeframe to TimeSync.

    Args:
        timeframe_id (str): Unique ID to reference the timeframe.
        utc_offset (str): UTC offset of the timeframe.
        start_time (datetime): start time of the timeframe.
        end_time (datetime): end time of the timeframe.
    """

    # If timeframe_id is None, provide default id (i.e. the timeframe's index).
    if timeframe_id is None:
        timeframe_id = f"Timeframe {len(TIMEFRAMES) - 1}"

    # Ensure that the same timeframe_id does not already exist in TIMEFRAMES.
    if timeframe_id in TIMEFRAMES.keys():
        print(f"\nA timeframe with ID \"{timeframe_id}\" already exists.")

        # Prompt the user whether they wish to overwrite the existing timeframe entry.
        response = input(f"\nDo you wish to overwrite the existing timeframe \"{timeframe_id}\"? [N/y]: ")
        if response.lower() not in ["y", "yes"]:
            print("\nAction aborted. Timeframe entry was not overwritten.")
            # End function execution.
            return

    # Create a new TimeFrame object.
    new_timeframe = TimeFrame(utc_offset, start_time, end_time)

    # Add the new timeframe to the "timeframes" dictionary.
    TIMEFRAMES[timeframe_id] = new_timeframe

    # Print success message.
    print("Timeframe added.\n")


def find_shared_timeframe() -> Tuple[datetime, datetime] | None:
    """ Finds the longest shared timeframe within the provided timeframes.

    Returns:
        a tuple containing the start and end times of the shared timeframe. None if a shared timeframe does not exist.
    """

    # Create a list containing just the timeframe objects (the value attributes) from the TIMEFRAMES dictionary.
    timeframes = list(TIMEFRAMES.values())

    # Initialize (latest_start_time, earliest_end_time) to the normalized (start, end) times of the 0th timeframe.
    latest_start_time, earliest_end_time = timeframes[0].get_norm_times()

    # Looping through every timeframe to find the latest normalized start time and earliest normalized end time.
    for timeframe in timeframes[1:]:
        # Get the normalized start and end times for the TimeFrame object.
        norm_start, norm_end = timeframe.get_norm_times()

        # Assign the current timeframe's normalized start time to latest_start_time if it is later.
        if norm_start > latest_start_time:
            latest_start_time = norm_start

        # Assign the current timeframe's normalized end time to earliest_end_time if it is earlier.
        if norm_end < earliest_end_time:
            earliest_end_time = norm_end

    # If the latest start time is greater than the earliest end time, a shared timeframe does not exist.
    if latest_start_time > earliest_end_time:
        return None

    # Else, return the start and end times as a tuple.
    else:
        return latest_start_time, earliest_end_time


def remove_timeframe(timeframe_id: str) -> bool:
    """ Remove a timeframe from TimeSync.

    Args:
        timeframe_id (str): ID of the timeframe to be removed.

    Returns:
        True if the timeframe was removed successfully.
    """

    # Check if the timeframe-id provided exists.
    if timeframe_id not in TIMEFRAMES.keys():
        print(f"remove: Timeframe with the ID \"{timeframe_id}\" does not exist.\n")
        return False

    # Remove the timeframe if all validation checks are passed.
    TIMEFRAMES.pop(timeframe_id)
    print(f"Timeframe \"{timeframe_id}\" removed.")
    return True


def reset() -> bool:
    """ Clears all stored timeframes.

    Returns:
        True if all timeframes were removed successfully.
    """

    # Prompt the user for confirmation.
    print("Are you sure you want to reset this session? This will clear all stored timeframes. [N/y]\n")
    response = input(">> ")

    if response.lower() in ["y", "yes"]:
        # Clearing all values in TIMEFRAMES.
        TIMEFRAMES.clear()
        print("Removed all timeframes.\n")
        return True

    else:
        return False


def list_timeframes() -> None:
    """ Prints a table of UTC offsets, start/end times and normalized start/end times of the timeframes. """

    # Creating the timeframes table as a multiline string.
    timeframes_table = construct_timeframe_table(TIMEFRAMES)

    # Print the timeframes table.
    print(timeframes_table)


def print_help(print_divider: bool = False) -> None:
    """ Prints the help description.

    Args:
        print_divider (bool): prints a divider after the help message if True.
    """

    # Print help description.
    print(HELP_DESCRIPTION)

    # Print a divider, if required.
    if print_divider:
        print(f"{('_' * 80)}\n")


def main():
    # Clear the terminal.
    clear_screen()

    # Print the title.
    print("\nTimeSync")

    # Print help.
    print_help(print_divider=True)

    while True:
        # Prompt the user for command.
        command = input(">> ")

        # If command is empty, continue.
        if command == "":
            continue

        # Split the command string into a list. Whitespace is the delimiter character.
        command = command.split()
        # The first string is the action to perform.
        action = command[0]

        # Spacing.
        print()

        """ Analyzing Command """
        # ADD
        if action == "add":
            # Number of arguments: Min number of arguments: 6. Max number of arguments: 7.
            if len(command) not in [6, 7]:
                print(f"\nadd: Expected 6 or 7 arguments but found {len(command) - 1}."
                      f"\n     Required arguments: timeframe-id, utc-offset, start-date, start-time, end-date, end-time"
                      )
                continue

            # Breakdown the command.
            timeframe_id = command[1]

            # Format UTC offset string.
            try:
                utc_offset = format_utc_offset(command[2])
            except ValueError as ve:
                print(f"utc-offset: {ve}\n")
                continue

            # Format start time string.
            try:
                start_time = f"{command[3]} {format_time(command[4])}"
            except ValueError as ve:
                print(f"start-time: {ve}\n")
                continue

            # Format end time string.
            try:
                # If 6 arguments are provided, use the start date as the end date.
                end_time = f"{command[3] if len(command) == 6 else command[5]} {format_time(command[-1])}"
            except ValueError as ve:
                print(f"end-time: {ve}\n")
                continue

            # Validate utc-offset format.
            flag, error_message = is_valid_offset(utc_offset)
            if flag is False:
                print(f"\nadd: {error_message}\n")
                continue

            # Validate start-time format.
            if not is_valid_datetime(start_time):
                print("\nadd: Incorrect format of start-time argument. Expected format: DD-MM-YY HH:MM.\n")
                continue

            # Validate end-time format.
            if not is_valid_datetime(end_time):
                print("\nadd: Incorrect format of end-time argument. Expected format: DD-MM-YY HH:MM.\n")
                continue

            # Try to parse start_time string to datetime object.
            try:
                # Create datetime object for start time.
                start_time = datetime.strptime(start_time, DATETIME_FORMAT)
            except ValueError:
                print("Illegal start-time argument.")
                continue

            # Try to parse end_time string to datetime object.
            try:
                # Create datetime object for end time.
                end_time = datetime.strptime(end_time, DATETIME_FORMAT)
            except ValueError:
                print("Illegal end-time argument.")
                continue

            # Add the timeframe if it passes all the validation checks.
            add_timeframe(timeframe_id=timeframe_id,
                          utc_offset=utc_offset,
                          start_time=start_time,
                          end_time=end_time)
        # ---------- #

        # FIND / RUN / SYNC
        elif action in ["find", "run", "sync"]:
            # Ensure there are more than 1 timeframes provided.
            if len(TIMEFRAMES) <= 1:
                print(f"\nfind:{len(TIMEFRAMES)} timeframe(s) provided."
                      "\n      Provide at least 2 timeframes to find a shared timeframe.")
                continue

            # Find the shared timeframe.
            shared_timeframe = find_shared_timeframe()

            # If None, shared time frame does not exist.
            if shared_timeframe is not None:
                # Split the shared timeframe tuple.
                start_datetime, end_datetime = shared_timeframe

                # Convert the datetime objects to strings.
                start_datetime = datetime.strftime(start_datetime, DATETIME_FORMAT)
                end_datetime = datetime.strftime(end_datetime, DATETIME_FORMAT)

                # Print output.
                print(f"Shared timeframe from {start_datetime} to {end_datetime} UTC+00:00.\n")

            else:
                print("No shared timeframe exists among the timeframes provided.\n")
        # ---------- #

        # REMOVE
        elif action == "remove":
            # Check number of arguments.
            if len(command) < 2:
                print(f"\nremove: Expected 1 argument \"timeframe-id\" but found 0 arguments.")
                continue

            # Remove the timeframe.
            remove_timeframe(timeframe_id=command[1])
        # ---------- #

        # RESET
        elif action == "reset":
            reset()
        # ---------- #

        # LIST
        elif action in ["ls", "list"]:
            list_timeframes()
        # ---------- #

        # VISUALIZE
        elif action == "vis":
            pass
        # ---------- #

        # CLEAR
        elif action == "clear":
            clear_screen()
        # ---------- #

        # HELP
        elif action == "help":
            # Print help.
            print_help()
        # ---------- #

        # EXIT
        elif action in ["X", "exit", "quit"]:
            # Prompt the user for confirmation.
            print("Are you sure you want to exit TimeSync? [N/y]")
            response = input(">> ")

            if response.lower() in ["y", "yes"]:
                break
        # ---------- #

        # INVALID COMMAND
        else:
            print("Invalid command.")

    # Exit the program.
    sys.exit(0)


if __name__ == "__main__":
    main()
