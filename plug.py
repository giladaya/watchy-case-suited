base_model_path = './Micro_USB_Cover_base.step'

p_width = 9.6
p_height = 5.2
p_wall_th = 0.8
p_length = 5
p_ledge_w = 0.4
p_ledge_th = 0.3
p_hole_depth = 0.8

base_width = 8.5
base_height = 3.65
base_th = 1

th = p_wall_th + p_hole_depth

base = (cq.importers.importStep(base_model_path)
  .translate((-base_width / 2, -base_th, -base_height / 2))
)

#outer shell
oshell = (cq.Workplane("XZ")
  .rect(p_width, p_height)
  .extrude(-th)
  .edges("|Y")
  .fillet(p_height * 0.45)
  .edges("|Z")
  .fillet(th * 0.45)
)

ledge = (cq.Workplane("XZ")
  .rect(p_width, p_height + 2 * p_ledge_w)
  .extrude(-th + p_ledge_th)
  .edges("|Y")
  .fillet((p_height + p_ledge_w) * 0.45)
)
#oshell = oshell.union(ledge)

ishell = (oshell.faces("<Y").workplane(p_wall_th, True)
    .rect((p_width - 2 * p_wall_th),(p_height - 2 * p_wall_th))
    .extrude(p_hole_depth, False)
    .edges("|Y")
    .fillet((p_height - p_wall_th) * 0.4)
)

box = oshell.cut(ishell)

full = base.union(box)

bounding = (cq.Workplane("XZ")
  .rect(p_width + p_ledge_w * 2, p_height + p_ledge_w * 2)
  .extrude(-p_length)
)

result = full.intersect(bounding).rotate((0,0,0),(1,0,0), 90)

#return the combined result
show_object(result)
cq.exporters.export(result, "micro-usb-plug.stl")
