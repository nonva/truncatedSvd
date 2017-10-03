import os, sys, ctypes
import numpy as np

class params(ctypes.Structure):
    _fields_  = [('X_n', ctypes.c_int),
            ('X_m', ctypes.c_int),
            ('k', ctypes.c_int)
    ]

curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
dll_path = [os.path.join(sys.prefix, 'scl'), os.path.join(curr_path, '../lib/')]

if os.name == 'nt':
    dll_path = [os.path.join(p, 'scl.dll') for p in dll_path]
else:
    dll_path = [os.path.join(p, 'libscl.so') for p in dll_path]

lib_path = [p for p in dll_path if os.path.exists(p) and os.path.isfile(p)]

if len(lib_path) is 0:
    print('Could not find shared library path at the following locations:')
    print(dll_path)

# Fix for GOMP weirdness with CUDA 8.0
try:
    ctypes.CDLL('libgomp.so.1', mode=ctypes.RTLD_GLOBAL)
except:
    pass
_mod = ctypes.cdll.LoadLibrary(lib_path[0])
_sparse_code = _mod.truncated_svd
_sparse_code.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double), params]

def as_fptr(x):
    return x.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

def truncated_svd(X, k):
    X = np.asfortranarray(X, dtype=np.float64)
    Q = np.empty((X.shape), dtype=np.float64, order='F')
    w = np.empty(k, dtype=np.float64)
    param = params()
    param.X_m = X.shape[0]
    param.X_n = X.shape[1]
    param.k = k

    _sparse_code(as_fptr(X), as_fptr(Q), as_fptr(w), param)

    return Q, w
