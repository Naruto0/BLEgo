# The MIT License (MIT)

# Copyright (c) 2015 

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bpy, colorsys

'''BLEgo lets you to iterate through your raw lego materials
and convert them to decent cycles alternatives, make sure all other materials in scene start with "_" !!!!'''

def filter(name):
    ''' Filer out other materials'''
    if name.startswith("_"):
        return False
    else:
        return True

def findType(name):
    ''' Return type of material based on prefix '''
    if name.startswith("Trans"):
        return "Transparent"
    elif name.startswith("Metallic"):
        return "Metallic"
    else:
        return "Plastic"

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

class ChangePlastic(ChangeMat):
    def __init__(self, material):
        ''' Change material of Diffused color and add glossiness to make use of cycles engine'''
        super(ChangePlastic, self).__init__(material)

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
        super(ChangeTrans, self).__init__(material)
        
    def setNodes(self):
        ''' Set subclass specific nodes '''
        self.node_glass = self.nodes.new(type='ShaderNodeBsdfGlass')
        self.node_glass.location = 100,0
        self.node_glass.inputs[0].default_value = self.color

        self.link_1 = self.links.new(self.node_glass.outputs[0], self.node_output.inputs[0])

class ChangeMetal(ChangePlastic):
    ''' Change Plastic to Metallic'''
    def __init__(self, material):
        super(ChangeMetal, self).__init__(material)

    def setMixer(self):
        self.node_mix.inputs[0].default_value = (0.75)

def main():
    '''Iterate through materials, change to cycles eye pleasing ones'''
    for material in bpy.data.materials[:]:
        # filter out names starting with "_" 
        if filter(material.name):
            # use other sublass for each material type here
            material_type = findType(material.name)

            # if "Trans" prefix
            if material_type == "Transparent":
                # debug: print(material)
                t = ChangeTrans(material) # Create material handling class (Transparent)
                t.set() # set default values
                t.setNodes() # set subclass specific data

            # if "Metallic" prefix
            elif material_type == "Metallic":
                m = ChangeMetal(material)
                m.set()
                m.setNodes()
                m.setMixer()

            # Diffused with little glossines here at the end
            else:
                # debug: print(material)
                d = ChangePlastic(material) # Create material handling class (Diffused)
                d.set() # set default parent class values
                d.setNodes() # 
        else:
            pass

if __name__ == '__main__':
    main()
