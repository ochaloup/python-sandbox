import logging
import time
import rx
import threading
import multiprocessing
import rx.operators as rxop
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler

logging.basicConfig(level=logging.INFO)

logging.info('ahoj')

def on_next_pulse(number) -> None:
    print(f'[{threading.get_ident()}] Start of {number}')
    time.sleep(1)
    print(f'[{threading.get_ident()}] End of {number}')
    # if number == 2:
    #     raise ValueError('Franta jede na skejtu')
    if number == 2:
        raise Exception('This is Exception!')

def error_handler(exception, scheduler):
    print(f'error handler::: {exception}')
    raise exception
   

def observable_pipeline_error_reporter(ex: Exception, _: rx.core.observable.observable.Observable) -> rx.core.observable.observable.Observable:
    logging.error(f"Intercepted error in observable pipeline: {ex}")
    raise ex

def rethrow_err(ex: Exception):
    print(f'HEEERE we are with {ex}')
    raise ex

print(f'[{threading.get_ident()}] Program is starting')


sch = ThreadPoolScheduler(multiprocessing.cpu_count())

# rx.of(1,2,3)
# rx.interval(1)
rx.interval(1).pipe(
    rxop.observe_on(sch),
    rxop.start_with(-1),
    # rxop.catch(rx.of(4)),
    rxop.do_action(on_next_pulse),
    rxop.catch(error_handler),
    rxop.retry(2),
# ).subscribe(on_next=lambda i: print(f"[{threading.get_ident()}] Printing {i}"), on_error=lambda e: print(f'[{threading.get_ident()}] error error! {e}'), on_completed=lambda: print('ok!'))
).subscribe(on_next=lambda i: print(f"[{threading.get_ident()}] Printing {i}"), on_error=rethrow_err)


input('Press a key to stop the program...\n')