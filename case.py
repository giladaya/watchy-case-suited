# import importlib
# import cadquery as cq
from watchy_sizes import *

# path to Watchy model downloaded from https://github.com/sqfmi/watchy-hardware/raw/main/3D/Watchy.step
watchy_model_path = '../Watchy.step'
show_watchy = False

# ------------
# Main params
# ------------
p_strap_width = 22 + 0.5 # strap width inc. tolerance
p_strap_dia = 4.0 # diameter of strap edge
p_layer_th = 0.12 # Thickness of print layer
p_flipTop = True # should flip the top

# Screws
p_num_screw_holes = 2 #Screws on each side (1 or 2)
p_screwpostID = 1.5 #Inner Diameter of the screw post holes, should be roughly screw diameter not including threads
p_boreDiameter = 4.5 #Diameter of the counterbore hole, if any
p_boreDepth = 0.5 #Depth of the counterbore hole, if
p_countersinkDiameter = 2.6 #Outer diameter of countersink.  Should roughly match the outer diameter of the screw head
p_countersinkAngle = 60.0 #Countersink angle (complete angle between opposite sides, not from center to one side)

# ------------
# Other params
# ------------
# New params
p_tolerance = 0.5 # Tolerance for pcb w / h
p_ledge_h = pcb_y_to_slot + pcb_slot_h + 1.5 # top and bottom inner "ledge"
p_tbar_hole_r = 0.6 # Radius of t-bar pin
p_under_pcb_depth = 8.0 # space for battery, etc.
p_inset_depth = pcb_t # depth of inset for pcb
p_fastener_width = p_strap_width - p_tolerance # width of fasteners

# Cover params
p_screen_th = 1.2 # thickness of screen (including adhesive tape)
p_top_sheet_th = 0.6 # thickness of top "cover sheet" - should be as thin as possible
p_screen_from_pcb_top = 4.0
p_screen_h = 38.0 # height of screen module
p_screen_w = 32.0 # width of screen module
p_screen_margin = 0.6 # margin of actual screen from module edge
p_screen_window_size = p_screen_w - 2.0 * p_screen_margin

# orginal parameter definitions
p_thickness =  1.0 #Thickness of the box walls

pcb_inset_width = pcb_w
pcb_inset_height = pcb_h

p_outerWidth = pcb_inset_width + 2.0 * p_thickness # Total outer width of box enclosure
p_outerLength = pcb_inset_height #Total outer length of box enclosure
p_outerHeight = p_under_pcb_depth + p_thickness + p_inset_depth #Total outer height of box enclosure

p_sideRadius = pcb_radius #Radius for the curves around the sides of the box
p_topAndBottomRadius =  p_outerHeight * 0.7 #Radius for the curves on the top and bottom edges of the box
p_topAndBottomRadiusInner =  p_outerHeight * 0.5

# Calculated
top_th = p_screen_th + p_top_sheet_th

# ------------
# Load Watchy model
# ------------
if show_watchy:
  watchy = cq.importers.importStep(watchy_model_path)
  watchy = (watchy
    .rotateAboutCenter((0,1,0), 180)
    .translate((-pcb_w / 2.0 + 0.8, -pcb_h / 2.0, p_outerHeight - p_inset_depth - 0.5))
  )
  debug(watchy)

# ------------
# Create model
# ------------
#outer shell
oshell = (cq.Workplane("XY")
  .rect(p_outerWidth, p_outerLength)
  .extrude(p_outerHeight)
)

#weird geometry happens if we make the fillets in the wrong order
if p_sideRadius > p_topAndBottomRadius:
    oshell = oshell.edges("|Z").fillet(p_sideRadius)
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
else:
    #oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
    #oshell = oshell.edges(cq.NearestToPointSelector((0,0,0))).fillet(p_topAndBottomRadius)
    oshell = oshell.edges("#Z and(not(>Z))").fillet(p_topAndBottomRadius)
    oshell = oshell.edges("|Z").fillet(p_sideRadius)

#inner shell
ishell = (oshell.faces("<Z").workplane(p_thickness, True)
    .rect((p_outerWidth - 4.0 * p_thickness),(pcb_h - 2.0*p_ledge_h))
    .extrude((p_outerHeight - p_thickness),False) #set combine false to produce just the new boss
)
ishell = (ishell.edges("|Z")
  .fillet(p_sideRadius - p_thickness)
  .edges(cq.NearestToPointSelector((0,0,0)))
  .fillet(p_topAndBottomRadiusInner)
)

#make the box outer box
box = oshell.cut(ishell)
# Emboss initials
box = (box
  .faces(cq.NearestToPointSelector((0,0,p_thickness)))
  .workplane()
  .text("//GD", 5, -3.0 * p_layer_th, cut=True, kind='bold', font='Courier')
)

# side cuts (buttons, etc)
pcb_top = pcb_h / 2.0
pcb_top_to_top_button = 7.5
top_button_to_usb = 7.75
usb_to_bottom_button = 6.5
button_width  = 4.6
button_height = 2.0
usb_b_width  = 7.4
usb_b_height = 3.0

holes_left = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button - button_height), p_outerHeight)
  .vLine(-p_inset_depth)
  .tangentArcPoint((-button_height, -button_height))
  .hLine(-button_width)
  .hLine(-(top_button_to_usb - (usb_b_height - button_height)))
  .line(-(usb_b_height - button_height), -(usb_b_height - button_height))
  .hLine(-usb_b_width)
  .line(-(usb_b_height - button_height), (usb_b_height - button_height))
  .hLine(-(usb_to_bottom_button - (usb_b_height - button_height)))
  .hLine(-button_width)
  .tangentArcPoint((-button_height, button_height))
  .vLine(p_inset_depth)
  .close()
  .extrude(-p_outerWidth / 2.0 + p_thickness)
)

top_button_to_vib = 5.5
vib_to_bottom_button = 6.0
vib_motor_width  = 10.0
vib_motor_height = 2.8

holes_right = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button - button_height), p_outerHeight)
  .vLine(-p_inset_depth)
  .tangentArcPoint((-button_height, -button_height))
  .hLine(-button_width)
  .hLine(-(top_button_to_vib - (vib_motor_height - button_height)))
  .line(-(vib_motor_height - button_height), -(vib_motor_height - button_height))
  .hLine(-vib_motor_width)
  .line(-(vib_motor_height - button_height), (vib_motor_height - button_height))
  .hLine(-(vib_to_bottom_button - (vib_motor_height - button_height)))
  .hLine(-button_width)
  .tangentArcPoint((-button_height, button_height))
  .vLine(p_inset_depth)
  .close()
  .extrude(p_outerWidth / 2.0 - p_thickness)
)

bHoles_left = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button), p_outerHeight + 1.0)
  .vLine(-1.0 -p_inset_depth - button_height)
  .hLine(-button_width)
  .vLine(p_inset_depth + button_height)
  .hLine(-(top_button_to_usb - (usb_b_height - button_height)))
  .vLine(-p_inset_depth - button_height)
  .line(-(usb_b_height - button_height), -(usb_b_height - button_height))
  .hLine(-usb_b_width)
  .line(-(usb_b_height - button_height), (usb_b_height - button_height))
  .vLine(p_inset_depth + button_height)
  .hLine(-(usb_to_bottom_button - (usb_b_height - button_height)))
  .vLine(-p_inset_depth - button_height)
  .hLine(-button_width)
  .vLine(p_inset_depth + button_height + 1.0)
  .close()
  .extrude(-p_outerWidth / 2.0)
)

bHoles_right = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button), p_outerHeight + 1.0)
  .vLine(-1.0 -p_inset_depth - button_height)
  .hLine(-button_width)
  .vLine(p_inset_depth + button_height)
  .hLine(-(top_button_to_usb + usb_b_width + usb_to_bottom_button))
  .vLine(-p_inset_depth - button_height)
  .hLine(-button_width)
  .vLine(p_inset_depth + button_height + 1.0)
  .close()
  .extrude(p_outerWidth / 2.0)
)

with_side_holes = (box
  .cut(holes_left)
  .cut(holes_right)
  .cut(bHoles_left)
  .cut(bHoles_right)
)

# pcb inset
slot_post_dia = pcb_slot_h - 0.1
pcb_inset = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .rect(pcb_inset_width, pcb_inset_height)
  .moveTo(0,0)
  .rect(pcb_w - 2.0 * pcb_x_to_slot - pcb_slot_h, pcb_h - 2.0 * pcb_y_to_slot - pcb_slot_h, forConstruction=True)
  .vertices()
  .circle(slot_post_dia / 2.0)
  .extrude(-p_inset_depth)
  .edges("|Z")
  .fillet(pcb_radius)
)
with_inset = with_side_holes.cut(pcb_inset)

# Top cover
if p_num_screw_holes == 1:
  fastener_hole_points = [(0, p_outerHeight * 0.75 - 0.5)]
elif p_num_screw_holes == 2:
  fastener_hole_points = [
    (-p_fastener_width * 0.3, p_outerHeight * 0.75 - 0.5),
    (p_fastener_width * 0.3, p_outerHeight * 0.75 - 0.5)
  ]
else:
  raise ValueError("screw_holes must be either 1 or 2.")

# basic shape
top = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .rect(p_outerWidth, p_outerLength)
  .extrude(top_th)
  .edges("|Z")
  .fillet(pcb_radius)
)  
# poles
poleCenters = [
  (0, pcb_h / 2.0 - pcb_y_to_slot - pcb_slot_h / 2.0), 
  (0, -(pcb_h / 2.0 - pcb_y_to_slot - pcb_slot_h / 2.0))
]
pole_thickness = pcb_slot_h - 0.6
pole_hole_depth = p_outerHeight / 2.0 + 0.5

top = (top.faces("<Z")
  .workplane(offset=0)
  .pushPoints(poleCenters)
  .rect(p_fastener_width, pole_thickness)
  .extrude(pole_hole_depth)
  .faces("<Z")
  .edges("|Y")
  .fillet(pole_thickness)
  .faces(">Y")
  .workplane(origin=(0, 0, 0), offset=0.0)
  .pushPoints( fastener_hole_points )
  # make the hole in the cover wider than the screw
  # so the top won't deform 
  .hole(p_screwpostID + 0.7, p_outerLength)
)
# screen holes
top_fillets = 0.75
window_cy = 3.05
top = (top.faces(">Z")
  # inset
  .workplane(origin=(0, pcb_inset_height/2.0 - p_screen_from_pcb_top - p_screen_h / 2.0, 0), offset=-p_top_sheet_th)
  .rect(p_screen_w + p_tolerance, p_screen_h)
  .cutBlind(-p_screen_th)
   # window
  .faces(">Z")
  .workplane(origin=(0, window_cy, 0), offset=0)
  .rect(p_screen_window_size, p_screen_window_size)
  .cutBlind(-p_screen_th)
  .faces(cq.selectors.BoxSelector(
    (-p_screen_w/2.0, -p_screen_h/2.0, 0), 
    (p_screen_w/2.0, p_screen_h/2.0, p_outerHeight*2.0),
    boundingbox=True
  ))
  .edges("|Z")
  .fillet(top_fillets)
  # Circumference fillet
  .faces(">Z")
  .edges(
    cq.selectors.InverseSelector(
      cq.selectors.BoxSelector(
        (-p_screen_w/2.0, -p_screen_h/2.0, 0), 
        (p_screen_w/2.0, p_screen_h/2.0, p_outerHeight*2.0),
        boundingbox=True
      )
    )
  )
  .fillet(1.0)
)

# decorations
top_b = (top.faces(">Z")
  .workplane(origin=(0, 0, 0), offset=0)
  .pushPoints( [ 
    (0, -pcb_inset_height/2.0 + 3.0, 0),
    (0, pcb_inset_height/2.0 - 3.0, 0)
  ])
  .rect(p_strap_width ,3.0)
  .extrude(4.0 * p_layer_th, taper=60)
  #.cutBlind(-0.5, taper=60)
)

debug(top)

pole_sockets = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .pushPoints(poleCenters)
  .rect(p_fastener_width + p_tolerance, pole_thickness + p_tolerance)
  #.extrude(-(pole_hole_depth  + p_tolerance / 2.0))
  .extrude(-p_outerHeight)
)

with_top_holes = (with_inset
  .faces("|Y and >Y")
  .workplane(origin=(0, 0, 0), offset=0.0)
  .pushPoints( fastener_hole_points )
  #.hole(p_screwpostID, p_outerLength)
  #.cboreHole(p_screwpostID, p_boreDiameter, p_boreDepth)
  .cskHole(p_screwpostID, p_countersinkDiameter, p_countersinkAngle)
  .faces("|Y and <Y")
  .workplane(origin=(0, 0, 0), offset=0.0)
  .pushPoints( fastener_hole_points )
  #.hole(p_screwpostID, p_outerLength)
  #.cboreHole(p_screwpostID, p_boreDiameter, p_boreDepth)
  .cskHole(p_screwpostID, p_countersinkDiameter, p_countersinkAngle)
  .cut(pole_sockets) 
)

# Strap Lugs
tbar_hole_depth = 1.5
lugs_th = 2.5
lugs_width = p_strap_width + 2.0 * lugs_th
lugs_dia = 5.0
lugs_length = p_outerHeight / 2.0 - 2.5
lugs = (cq.Workplane("ZY")
  .workplane(
    origin=(0, -p_outerLength / 2.0, p_outerHeight - p_inset_depth), 
    offset=lugs_width / 2.0)
  .line(-lugs_length, -lugs_length)
  .tangentArcPoint((-lugs_dia, lugs_dia))
  .line(lugs_length, lugs_length)
  .close()
  .extrude(-lugs_th)
  .faces("<X")
  .edges()
  .fillet(lugs_th/2.0)
  # tbar holes
  .faces(">X")
  .workplane(
    origin=(0, -p_outerLength / 2.0 - p_outerHeight * 0.25 + 1.25, p_outerHeight * 0.25 - p_inset_depth + 2.0), 
    offset=(-tbar_hole_depth))
  .circle(p_tbar_hole_r)
  .cutBlind(tbar_hole_depth) 
  #.extrude(p_strap_width + tbar_hole_depth * 2.0)
  .mirror("ZY", union=True)
  .mirror("XZ", union=True)
)
#debug(lugs)
with_top_holes = with_top_holes.union(lugs)

if p_flipTop:
  top = (top
    .translate((-p_outerWidth - 1.0, 0, -(p_outerHeight+top_th)))
    .rotate((0,0,0),(0,1,0), 180)
    #.rotate((0,0,0),(0,1,0), 90)
    #.translate((p_outerWidth/2.0, 0, (p_outerWidth/2.0)))
)
else:
  top = (top
    .translate((-p_outerWidth - 1.0, 0, -(p_outerHeight-pole_hole_depth)))
  )

result = (with_top_holes
  .union(top)
)

#return the combined result
show_object(result)
cq.exporters.export(result, "watchy-wide.stl")
cq.exporters.export(top, "watchy-wide-top.stl")
cq.exporters.export(with_top_holes, "watchy-wide-body.stl")
