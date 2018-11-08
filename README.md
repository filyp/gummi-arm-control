# gummi-arm-control

## TODO

* express marker position in space as quaternion
    * will be possible to measure arm position from any place
    * will be possible to estimate how confident is the readout
* add mapping: (angle, stiffness) -> (confidence)
* build neural network
    * use Levenberg-Marquardt backpropagation with single hidden layer
* use histograms to estimate how good is the readout
* use logger instead of printing