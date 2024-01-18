"""Monitor the tasks stored in the .json file logged with the API."""
import os
import json

import inductiva

PATH_TO_JSON = "/Path/to/task_metadata.json"
DOWNLOAD_TASKS = True


def main():
    json_lines = []
    with open(PATH_TO_JSON, "r", encoding="utf-8") as json_file:
        for line in json_file:
            json_lines.append(json.loads(line))

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
