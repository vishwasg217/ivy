# global
from functools import reduce

# local
import ivy
from ivy import with_unsupported_dtypes
from ivy.functional.frontends.torch.func_wrapper import (
    to_ivy_arrays_and_back,
)


def _broadcast_pooling_helper(x, pool_dims: str = "2d", name: str = "padding"):
    dims = {"1d": 1, "2d": 2, "3d": 3}

    if isinstance(x, int):
        return tuple([x for _ in range(dims[pool_dims])])

    if len(x) == 1:
        return tuple([x[0] for _ in range(dims[pool_dims])])
    elif len(x) == dims[pool_dims]:
        return tuple(x)
    elif len(x) != dims[pool_dims]:
        raise ValueError(
            f"`{name}` must either be a single int, "
            f"or a tuple of {dims[pool_dims]} ints. "
        )


@to_ivy_arrays_and_back
def avg_pool1d(
    input,
    kernel_size,
    stride=None,
    padding=0,
    ceil_mode=False,
    count_include_pad=True,
):
    if stride is None:
        stride = kernel_size
    data_format = "NCW"
    # TODO: remove the broadcasting and padding string specification when ivy.avg_pool
    #   support explicit padding
    kernel_size = _broadcast_pooling_helper(kernel_size, "1d", name="kernel_size")
    padding = _broadcast_pooling_helper(padding, "1d", name="padding")
    if all(
            [pad == ivy.ceil((kernel - 1) / 2) for kernel, pad in zip(kernel_size, padding)]
    ):
        padding = "SAME"
    else:
        padding = "VALID"
    return ivy.avg_pool1d(
        input,
        kernel_size,
        stride,
        padding,
        data_format=data_format,
        count_include_pad=count_include_pad,
        ceil_mode=ceil_mode,
    )

@to_ivy_arrays_and_back
def avg_pool2d(
    input,
    kernel_size,
    stride=None,
    padding=0,
    ceil_mode=False,
    count_include_pad=True,
    divisor_override=None,
):
    if stride is None:
        stride = kernel_size
    data_format = "NCHW"
    # TODO: remove the broadcasting and padding string specification when ivy.avg_pool
    #   support explicit padding
    kernel_size = _broadcast_pooling_helper(kernel_size, "2d", name="kernel_size")
    padding = _broadcast_pooling_helper(padding, "2d", name="padding")
    if all(
            [pad == ivy.ceil((kernel - 1) / 2) for kernel, pad in zip(kernel_size, padding)]
    ):
        padding = "SAME"
    else:
        padding = "VALID"
    return ivy.avg_pool2d(
        input,
        kernel_size,
        stride,
        padding,
        data_format=data_format,
        ceil_mode=ceil_mode,
        count_include_pad=count_include_pad,
        divisor_override=divisor_override,
    )


@to_ivy_arrays_and_back
def max_pool1d(input, kernel_size, stride=None, padding=0):
    kernel_size = _broadcast_pooling_helper(kernel_size, "1d", name="kernel_size")
    stride = _broadcast_pooling_helper(stride, "1d", name="stride")
    padding = _broadcast_pooling_helper(padding, "1d", name="padding")
    kernel_pads = list(zip(kernel_size, padding))

    data_format = "NCW"

    if not all([pad <= kernel / 2 for kernel, pad in kernel_pads]):
        raise ValueError(
            "pad should be smaller than or equal to half of kernel size, "
            f"but got padding={padding}, kernel_size={kernel_size}. "
        )
    # figure out whether to apply padding
    if all([pad == ivy.ceil((kernel - 1) / 2) for kernel, pad in kernel_pads]):
        padding_str = "SAME"
    else:
        padding_str = "VALID"

    return ivy.max_pool1d(
        input, kernel_size, stride, padding_str, data_format=data_format
    )

@with_unsupported_dtypes({"2.0.1 and below": ("float16",)}, "torch")
@to_ivy_arrays_and_back
def max_unpool1d(input, indices, kernel_size, stride=None, padding=0, output_size=None):
    
    if stride is None:
        stride = kernel_size

    data_format = "NCW"

    return ivy.max_unpool1d(
        input, indices, kernel_size, stride, padding, data_format, output_size
    )


@with_unsupported_dtypes({"2.0.1 and below": ("float16",)}, "torch")
@to_ivy_arrays_and_back
def max_pool2d(
    input,
    kernel_size,
    stride=None,
    padding=0,
    dilation=1,
    ceil_mode=False,
    return_indices=False,
):
    # ToDo: Add return_indices once superset in implemented
    dim_check = False
    if input.ndim == 3:
        input = input.expand_dims()
        dim_check = True
    if not stride:
        stride = kernel_size
    ret = ivy.max_pool2d(
        input,
        kernel_size,
        stride,
        padding,
        data_format="NCHW",
        dilation=dilation,
        ceil_mode=ceil_mode,
    )
    if dim_check:
        return ret.squeeze(0)
    return ret

@with_unsupported_dtypes({"2.0.1 and below": ("float16",)}, "torch")
@to_ivy_arrays_and_back
def max_unpool2d(input, indices, kernel_size, stride=None, padding=0, output_size=None):
    
    if stride is None:
        stride = kernel_size

    data_format = "NCHW"

    return ivy.max_unpool2d(
        input, indices, kernel_size, stride, padding, data_format, output_size
    )

@with_unsupported_dtypes({"2.0.1 and below": ("float16",)}, "torch")
@to_ivy_arrays_and_back
def max_unpool3d(input, indices, kernel_size, stride=None, padding=0, output_size=None):
    
    if stride is None:
        stride = kernel_size

    data_format = "NCDHW"

    return ivy.max_unpool3d(
        input, indices, kernel_size, stride, padding, data_format, output_size
    )

@to_ivy_arrays_and_back
def adaptive_max_pool2d(
    input,
    output_size,
    return_indices=False,
):
    # ToDo: Add return_indices once superset is implemented
    return ivy.adaptive_max_pool2d(input, output_size)


@with_unsupported_dtypes(
    {
        "2.0.1 and below": (
            "bfloat16",
            "float16",
        )
    },
    "torch",
)
@to_ivy_arrays_and_back
def adaptive_avg_pool1d(input, output_size):
    return ivy.adaptive_avg_pool1d(input, output_size)


@with_unsupported_dtypes(
    {
        "2.0.1 and below": (
            "float16",
            "bfloat16",
        )
    },
    "torch",
)
@to_ivy_arrays_and_back
def adaptive_avg_pool2d(input, output_size):
    return ivy.adaptive_avg_pool2d(input, output_size)


@with_unsupported_dtypes(
    {
        "2.0.1 and below": (
            "float16",
            "bfloat16",
        )
    },
    "torch",
)
@to_ivy_arrays_and_back
def lp_pool1d(input, norm_type, kernel_size, stride=None, ceil_mode=False):
    data_format = "NCW"
    padding = "VALID"
    if stride is None:
        stride = kernel_size
    if not isinstance(kernel_size, int):
        kernel_mul = reduce(lambda x, y: x * y, kernel_size)
    else:
        kernel_mul = kernel_size

    out = ivy.avg_pool1d(
        ivy.pow(input, norm_type),
        kernel_size,
        stride,
        padding,
        data_format=data_format,
        ceil_mode=ceil_mode,
    )
    p = 1.0 / norm_type if norm_type != 0 else 1.0
    return ivy.pow(ivy.multiply(out, kernel_mul), p)


@to_ivy_arrays_and_back
def lp_pool2d(input, norm_type, kernel_size, stride=None, ceil_mode=False):
    data_format = "NCHW"
    padding = "VALID"
    if stride is None:
        stride = kernel_size
    out = ivy.avg_pool2d(
        ivy.pow(input, norm_type),
        kernel_size,
        stride,
        padding,
        data_format=data_format,
        ceil_mode=ceil_mode,
    )
    if not isinstance(kernel_size, int):
        kernel_mul = reduce(lambda x, y: x * y, kernel_size)
    else:
        kernel_mul = kernel_size
    p = ivy.divide(1.0, norm_type) if norm_type != 0 else 1.0
    return ivy.pow(ivy.multiply(out, kernel_mul), p).astype(input.dtype)


@to_ivy_arrays_and_back
def avg_pool3d(
    input,
    kernel_size,
    stride=None,
    padding=0,
    ceil_mode=False,
    count_include_pad=True,
    divisor_override=None,
):
    if stride is None:
        stride = kernel_size
    # TODO: remove the broadcasting and padding string specification when ivy.avg_pool
    #   support explicit padding
    kernel_size = _broadcast_pooling_helper(kernel_size, "3d", name="kernel_size")
    padding = _broadcast_pooling_helper(padding, "3d", name="padding")
    if all(
            [pad == ivy.ceil((kernel - 1) / 2) for kernel, pad in zip(kernel_size, padding)]
    ):
        padding = "SAME"
    else:
        padding = "VALID"
    return ivy.avg_pool3d(
        input,
        kernel_size,
        stride,
        padding,
        data_format="NCDHW",
        ceil_mode=ceil_mode,
        count_include_pad=count_include_pad,
        divisor_override=divisor_override,
    )
