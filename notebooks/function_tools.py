# Copyright 2022 Cognite AS
import time


def status_check(function):

    start_time = time.time()
    # Repeat until status is ready
    while function.status != "Ready":

        function.update()

        time_elapsed = int(time.time() - start_time)

        print(function.status + f". Waiting for {time_elapsed} seconds", end="\r")

        if function.status == "Failed":
            print("Failed to deploy function")
            break

        time.sleep(5)
    else:
        print(f"Function is successfully deployed. Wait time: {time_elapsed} seconds.")
