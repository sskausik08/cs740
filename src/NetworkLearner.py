# Doodling with neural networks. Not completely acquainted
from sknn.mlp import Classifier, Layer
import numpy as np
nn = Classifier(
    layers=[
        Layer("Sigmoid", units=100),
        Layer("Softmax")],
    learning_rate=0.02,
    n_iter=10)
X = np.array([[0, 1], [1, 0]])
Y = np.array([[1], [0]])
nn.fit(X,Y)
X = np.array([[1, 1], [1, 0]])
Y = np.array([[1], [0]])
nn.fit(X,Y)
out = nn.predict(np.array([[1, 1]]))
print out