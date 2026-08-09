import openseespy.opensees as ops
import sys

print("Testing OpenSeesPy...")
sys.stdout.flush()
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)
print("Model created.")
sys.stdout.flush()
ops.node(1, 0, 0)
print("Node 1 created.")
sys.stdout.flush()
print("Success.")
