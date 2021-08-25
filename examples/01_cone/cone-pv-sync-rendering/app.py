import sys

# -----------------------------------------------------------------------------
# Virtual Environment handling
# -----------------------------------------------------------------------------

if "--virtual-env" in sys.argv:
    virtualEnvPath = sys.argv[sys.argv.index("--virtual-env") + 1]
    virtualEnv = virtualEnvPath + "/bin/activate_this.py"
    exec(open(virtualEnv).read(), {"__file__": virtualEnv})

# -----------------------------------------------------------------------------

from pywebvue import App

from paraview import simple

# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

app = App("ParaView Remote Rendering", backend="paraview")
app.layout = "./template.html"
app.state = {
    "resolution": 6,
}
app.vue_use += ["vtk"]

# -----------------------------------------------------------------------------
# ParaView pipeline
# -----------------------------------------------------------------------------

view = simple.GetRenderView()
cone = simple.Cone()
representation = simple.Show(cone, view)
simple.ResetCamera()

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@app.change("resolution")
def update_cone():
    cone.Resolution = app.get("resolution")
    app.set("scene", app.scene(view))


# -----------------------------------------------------------------------------
# Main
# /opt/paraview/bin/pvpython ./examples/.../app.py --port 1234 --virtual-env ~/Documents/code/Web/vue-py/py-lib
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.on_ready = update_cone
    app.run_server()
