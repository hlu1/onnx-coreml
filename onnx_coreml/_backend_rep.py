from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import numpy as np

from onnx.backend.base import BackendRep, namedtupledict


class CoreMLRep(BackendRep):
    def __init__(self, coreml_model, useCPUOnly=False):
        super(CoreMLRep, self).__init__()
        self.model = coreml_model
        self.useCPUOnly = useCPUOnly

        spec = coreml_model.get_spec()
        self.input_names = [str(i.name) for i in spec.description.input]
        self.output_names = [str(o.name) for o in spec.description.output]

    def run(self, inputs, **kwargs):
        super(CoreMLRep, self).run(inputs, **kwargs)
        inputs_ = inputs
        _reshaped = False
        for i, input_ in enumerate(inputs_):
            shape = input_.shape
            if len(shape) == 4 or len(shape) == 2:
                inputs_[i] = input_[np.newaxis, :]
                _reshaped = True
        input_dict = dict(
            zip(self.input_names,
                map(np.array, inputs_)))
        prediction = self.model.predict(input_dict, self.useCPUOnly)
        output_values = [prediction[name] for name in self.output_names]
        for i, output_ in enumerate(output_values):
            shape = output_.shape
            if _reshaped and len(shape) == 5 and shape[1] == 1:
                # get rid of batch dimension
                output_values[i] = np.squeeze(output_, axis=1)
        return namedtupledict('Outputs',
                              self.output_names)(*output_values)
