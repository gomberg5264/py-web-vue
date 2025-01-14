import os
from pywebvue import App
from pywebvue.modules import VTK

from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch

# Grab implementation
import vtkmodules.vtkRenderingOpenGL2

# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

app = App("VTK contour - Remote/Local rendering")
app.state = {
    "data_range": [0, 1],
    "contour_value": 0,
    "override": "auto",
}
app.enableModule(VTK)

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

data_directory = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "data",
)
head_vti = os.path.join(data_directory, "head.vti")

reader = vtkXMLImageDataReader()
reader.SetFileName(head_vti)
reader.Update()

contour = vtkContourFilter()
contour.SetInputConnection(reader.GetOutputPort())
contour.SetComputeNormals(1)
contour.SetComputeScalars(0)

# Extract data range => Update store/state
data_range = reader.GetOutput().GetPointData().GetScalars().GetRange()
app.set("data_range", data_range)
app.set("contour_value", 0.5 * (data_range[0] + data_range[1]))

# Configure contour with valid values
contour.SetNumberOfContours(1)
contour.SetValue(0, app.get("contour_value"))

# Rendering setup
renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.SetSize(300, 300)
renderWindow.SetWindowName("rendering")
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
renderWindowInteractor.EnableRenderOff()

mapper = vtkPolyDataMapper()
actor = vtkActor()
mapper.SetInputConnection(contour.GetOutputPort())
actor.SetMapper(mapper)
renderer.AddActor(actor)
renderer.ResetCamera()
renderWindow.Render()

# Start with "local" rendering rather than "remote"
view = VTK.view(renderWindow, "demo", mode="local")

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@app.change("contour_value")
def update_contour(contour_value, **kwargs):
    contour.SetValue(0, contour_value)
    view.push_image()


# -----------------------------------------------------------------------------
# MAIN
#   /opt/paraview/bin/pvpython ./examples/.../app.py --port 1234 --virtual-env ~/Documents/code/Web/vue-py/py-lib
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.on_ready = view.push_geometry
    app.run_server()
