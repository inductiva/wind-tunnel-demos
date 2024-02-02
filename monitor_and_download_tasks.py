"""Monitor the tasks stored in the .json file logged with the API."""
import os
import json

import inductiva

PATH_TO_JSON = ""
DOWNLOAD_TASKS = False


def main():
    with open(PATH_TO_JSON, "r", encoding="utf-8") as json_file:
        lines = json_file.readlines()

    json_lines = [json.loads(line) for line in lines]

    task_counts = {}

    for json_line in json_lines:
        task_input_dir = json_line["input_dir"]
        task_id = json_line["task_id"]
        task = inductiva.tasks.Task(task_id)
        status = task.get_status()
        if status not in task_counts:
            task_counts[status] = 1
        else:
            task_counts[status] += 1

        if status == "success" and DOWNLOAD_TASKS:
            task.download_outputs(
                output_dir=os.path.join(task_input_dir, "downloaded_outputs"))

    print(task_counts)


if __name__ == "__main__":
    main()
