import sys

from chainer import cuda
from PyQt5 import QtWidgets

from chainer_wing.subwindows.train_config import TrainParamServer


def disp_error(message: str):
    error = QtWidgets.QErrorMessage()
    error.showMessage(message)
    error.exec_()


def check_cuda_available():
    try:
        cuda.check_cuda_available()
    except RuntimeError:
        disp_error("CUDA environment is not correctly set up. Confirm your "
                   "envirionment or change Train con figuration and set 'GPU'"
                   " 0.")
        return False
    return True


class ExistsInvalidParameter(Exception):
    pass


class AbnormalDataCode(Exception):
    pass


class UnexpectedFileExtension(Exception):
    pass


def get_executed_last_node():

    def get_last_lineno(stack):
        for frame in stack:
            if frame.f_code.co_filename != TrainParamServer().get_net_name():
                continue
            if frame.f_code.co_name == '__call__':
                last_lineno_candidate = frame.f_lineno
            if frame.f_code.co_name == '_predict':
                return frame.f_lineno
        return last_lineno_candidate

    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()

    lineno = get_last_lineno(stack)
    with open(TrainParamServer().get_net_name(), 'r') as net_file:
        for i, line in enumerate(net_file):
            if i == lineno-1:
                last_node = line.strip().split(' ')[0]
                last_node = last_node.replace('self.', '')
                break

    return last_node