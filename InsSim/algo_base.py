import numpy as np
class INS_ALGO:
    def __init__(self) -> None:
        self.a : np.ndarray
        self.g : np.ndarray
        try:
            self.alg_name
        except:
            raise ValueError("Inherited class from INS_ALGO should set alg_name")

    def run(self, time_sec):
        raise NotImplementedError()
    
    def get_results(self):
        '''
            return
        '''
        raise NotImplementedError()
