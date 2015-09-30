import bpy, colorsys

'''BLEgo lets you to iterate through your raw lego materials
and convert them to decent cycles alternatives, make sure all other materials in scene start with "_" !!!!'''

def filter(name):
    ''' Filer out other materials'''
    if name.startswith("_"):
        return False
    else:
        return True

def findTransp(name):
    ''' Return True if transparent (by name obviously)'''
    if name.startswith("Trans"):
        return True
    else:
        return False

def enhance(input_rgba):
    ''' Just pull saturation towards 1 using average value between original and 1'''
    R, G, B, A = input_rgba
    H, S, V = colorsys.rgb_to_hsv(R, G, B)
    if S == 0:
        S = S
    else:
        S = (S + 1) / 2
    nR, nG, nB = colorsys.hsv_to_rgb(H, S, V)
    rgba = (nR, nG, nB, A)
    
    return rgba

class ChangeMat(object):
    def __init__(self, material):
        ''' Base class to initiate shared values and variables '''
        self.material = material
        self.material.use_nodes = True
        
        self.nodes = self.material.node_tree.nodes
        self.links = self.material.node_tree.links
        self.material_color = self.material.node_tree.nodes['Diffuse BSDF'].inputs[0].default_value[:]
        self.color = enhance(self.material_color)
    
    def set(self):
        ''' set Initial node '''
        for node in self.nodes:
            self.nodes.remove(node)

        self.node_output = self.nodes.new(type='ShaderNodeOutputMaterial')
        self.node_output.location = 400, 0

class ChangeDiff(ChangeMat):
    def _init__(self, material):
        ''' Change material o f Diffused color and add glossiness to make use of cycles engine'''
        ChangeMat.__init__(self, material)

    def setNodes(self):
        ''' Set subclass specific nodes '''
        self.node_diffuse = self.nodes.new(type='ShaderNodeBsdfDiffuse')
        self.node_diffuse.location = -200, 100
        self.node_diffuse.inputs[0].default_value = self.color

        self.node_glossy = self.nodes.new(type='ShaderNodeBsdfGlossy')
        self.node_glossy.location = -200, -100

        self.node_mix = self.nodes.new(type='ShaderNodeMixShader')
        self.node_mix.location = 100, 0
        self.node_mix.inputs[0].default_value = (0.25)

        self.link_1 = self.links.new(self.node_diffuse.outputs[0], self.node_mix.inputs[1])
        self.link_2 = self.links.new(self.node_glossy.outputs[0], self.node_mix.inputs[2])
        self.link_3 = self.links.new(self.node_mix.outputs[0], self.node_output.inputs[0])

class ChangeTrans(ChangeMat):
    ''' Change material to transparent '''
    def __init__(self, material):
        ChangeMat.__init__(self, material)
        
    def setNodes(self):
        ''' Set subclass specific nodes '''
        self.node_glass = self.nodes.new(type='ShaderNodeBsdfGlass')
        self.node_glass.location = 100,0
        self.node_glass.inputs[0].default_value = self.color

        self.link_1 = self.links.new(self.node_glass.outputs[0], self.node_output.inputs[0])

def main():
    '''Iterate through materials, change to cycles eye pleasing ones'''
    for material in bpy.data.materials[:]:
        # filter out names starting with "_" 
        if filter(material.name):
            # use other sublass for each material transparent here
            if findTransp(material.name):
                # debug: print(material)
                t = ChangeTrans(material) # Create material handling class (Transparent)
                t.set() # set default values
                t.setNodes() # set subclass specific data

            # Diffused with little glossines here
            else:
                # debug: print(material)
                d = ChangeDiff(material) # Create material handling class (Diffused)
                d.set() # set default parent class values
                d.setNodes() # 
        else:
            pass

if __name__ == '__main__':
    main()
