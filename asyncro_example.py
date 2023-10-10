import asyncio 
import time

async def print_message(msg):
    await asyncio.sleep(1)
    print(msg)

async def print_message2(msg):
    time.sleep(2)
    await asyncio.sleep(3)
    print(msg)

## create event loop for 3 task schedulely running
async def print_concurrenly():
    start_time = time.time()
    await asyncio.create_task(print_message('task 3'))
    task_3 = time.time()
    print("done in: ", task_3 - start_time)

    ## create 2 tasks, not execute it
    t2 = asyncio.create_task(print_message2('task 2'))
    t1 = asyncio.create_task(print_message('task 1'))

    ## "handle" was given to task 2, when it come to sleep (after 2
    ## seconds for whole programm to sleep with time.sleep(2)), 
    ## "handle" will go to task 1. when task 1 come to sleep, "handle" don't find any available task (cuz task 2 still sleeping ), "handle' stay back at task 1 
    await t2 ## here start execute task 2
    print("done in: ", time.time() - start_time)

asyncio.run(print_concurrenly())