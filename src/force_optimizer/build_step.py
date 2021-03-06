from group import Group
import itertools


def start(force_algo, debug=False):

    create_groups(force_algo, debug)

    if debug:
        for group in force_algo.groups:
            print group

    find_special_groups(force_algo, debug)

    force_algo.groups = sorted(force_algo.groups, cmp=group_compare)

    find_special_pins(force_algo, debug)

    if debug:
        for group in force_algo.groups:
            print group

    find_neighbors(force_algo, debug)

    if debug:
        for group in force_algo.groups:
            print group

    for group in force_algo.groups:
        group.is_bias = is_bias_group(group, force_algo)

def group_compare(x, y):
    '''
    Sort groups by their group_id
    groups on the low level with long IDs came first
    '''
    return len(y.group_id) - len(x.group_id)

def find_special_groups(forceOptimizer, debug):
    new_groups = []
    new_level = 0
    for group in forceOptimizer.groups:
        if len(group.blocks):

            bias_blocks = []
            in_blocks = []

            for block in group.blocks:

                for pin in block.pins.values():
                    if pin.net.startswith("vbias"):

                        bias_blocks.append(block)
                        break
                    if pin.net.startswith("in"):
                        in_blocks.append(block)

            '''
            if len(bias_blocks) < len(group.blocks) and len(bias_blocks):
                new_group_id = group.group_id[:]
                new_group_id.append(len(group.childs))

                new_group = Group(new_group_id)
                if new_group not in new_groups:
                    new_level = len(new_group_id)
                    new_groups.append(new_group)
                    new_group.parent = group
                    group.childs.append(new_group)
                    new_group.is_bias_connected = True

                    for block in bias_blocks:
                        block.groups = new_group_id
                        group.blocks.remove(block)
                        new_group.blocks.add(block)

            if len(in_blocks) and len(in_blocks)< len(group.blocks):
                new_group_id = group.group_id[:]
                new_group_id.append(len(group.childs))

                new_group = Group(new_group_id)
                if new_group not in new_groups:
                    new_level = len(new_group_id)
                    new_groups.append(new_group)
                    new_group.parent = group
                    group.childs.append(new_group)

                    for block in in_blocks:
                        block.groups = new_group_id
                        group.blocks.remove(block)
                        new_group.blocks.add(block)
            '''
            if len(bias_blocks) < len(group.blocks) and len(bias_blocks):
                new_group_id = group.parent.group_id[:]
                new_group_id.append(len(group.parent.childs))

                new_group = Group(new_group_id)
                if new_group not in new_groups:
                    new_groups.append(new_group)
                    new_group.parent = group.parent
                    group.parent.childs.append(new_group)
                    new_group.is_bias_connected = True

                    for block in bias_blocks:
                        block.groups = new_group_id
                        group.blocks.remove(block)
                        new_group.blocks.add(block)

            if len(in_blocks) and len(in_blocks)< len(group.blocks):
                new_group_id = group.parent.group_id[:]
                new_group_id.append(len(group.parent.childs))

                new_group = Group(new_group_id)
                if new_group not in new_groups:
                    new_groups.append(new_group)
                    new_group.parent = group.parent
                    group.parent.childs.append(new_group)
                    new_group.is_bias_connected = True

                    for block in in_blocks:
                        block.groups = new_group_id
                        group.blocks.remove(block)
                        new_group.blocks.add(block)

    if new_level:
        for group in forceOptimizer.groups:
            if len(group.group_id) == new_level - 1:





                if len(group.blocks):

                    new_group_id = group.group_id[:]
                    new_group_id.append(len(group.childs))
                    new_group = Group(new_group_id)

                    if new_group not in new_groups:

                        new_groups.append(new_group)
                        new_group.parent = group
                        group.childs.append(new_group)
                        blocks = list(group.blocks)

                        for block in blocks:
                            print block.name
                            block.groups = new_group_id[:]
                            group.blocks.remove(block)
                            new_group.blocks.add(block)
    for group in new_groups:
        forceOptimizer.groups.append(group)

def is_bias_group(group, forceOptimizer):

    if len(group.blocks):

        vbias_net = set()
        for block in group.blocks:
            for pin in block.pins.values():
                if pin.net.lower() in forceOptimizer.bias_nets:
                    vbias_net.add(pin.net.lower())

        if vbias_net == forceOptimizer.bias_nets:
            return True
        else:
            return False
    else:
        return False

def find_special_pins (forceOptimizer, debug):
    for group in forceOptimizer.groups:
        group.connected_gnd = 0
        group.connected_vcc = 0
        group.connected_out = 0
        group.connected_inp = 0

        for block in group.blocks:
            #check the connection to important pins
            for p in block.pins.values():

                for pin in forceOptimizer.pins_south:
                    if p.net.lower().startswith(pin):
                        group.connected_gnd += 1
                        group.block_south.add(block)

                for pin in forceOptimizer.pins_north:
                    if p.net.lower().startswith(pin):
                        group.connected_vcc += 1
                        group.block_north.add(block)

                for pin in forceOptimizer.pins_east:
                    if p.net.lower().startswith(pin):
                        group.connected_out += 1
                        group.block_east.add(block)

                for pin in forceOptimizer.pins_west:
                    if p.net.lower().startswith(pin):
                        group.block_west.add(block)

                if p.net.lower().startswith("in"):
                    group.connected_inp  #+= 1

            if group.connected_out > 0:
                group.connected_parent_east += group.connected_out
            if group.connected_gnd > 0:
                group.connected_parent_south += group.connected_gnd
            if group.connected_vcc > 0:
                group.connected_parent_north += group.connected_vcc

        for child in group.childs:
            group.connected_gnd += child.connected_gnd
            group.connected_vcc += child.connected_vcc
            group.connected_out += child.connected_out
            group.connected_inp += child.connected_inp

        group.connected_parent_east = group.connected_out
        group.connected_parent_south = group.connected_gnd
        group.connected_parent_north = group.connected_vcc
def create_groups(forceOptimizer, debug=False):
    '''
    DESCRIPTION:   Create the groups and add them to the list: groups
    STATE:         finish
    '''

    if debug:
        print ""
        print "============="
        print "Create Groups"
        print "============="
        print ""

    #go through all blocks in circuit
    for block in forceOptimizer.blocks:

        group_id = block.groups  # the lowest group get all IDs
        if debug:
            pins = ""
            for p in block.pins.values():
                pins += " " + p.net
                print "Block: ", block.name, " Group ID", group_id, "Pins:", pins

        group = search_group(group_id,forceOptimizer)  # check if the group allready exists



        if group is None:  # create a new group if needed
            if debug:
                print ("Create a new Group with ID", group_id)
            group = Group(group_id)
            forceOptimizer.groups.append(group)

        if block.name.startswith('i'):
            group.block_north.add(block);
            group.block_west.add(block)



        #add the block to the low level group
        group.add_block(block)

        #if group has parents create them
        if len(group.group_id) > 1:
            create_parent(group, forceOptimizer, debug)
        #else add group to main group
        else:
            forceOptimizer.group_main.add_child(group)
            group.parent = forceOptimizer.group_main

def search_group(group_id, forceOptimizer):
    '''
    PARAMETER:  group_ids     is an array with the IDs of the parent Groups and the ID of the searched group
                return        the group if it exists, else None
    STATE:      not finish
    '''
    for group in forceOptimizer.groups:
        if group.group_id == group_id:
            return group
    return None

def create_parent(child, forceOptimizer, debug):
    '''
    DESCRIPTION:    builds recursive the parents of the groupe, which containts the block
                    when the algo reached the last parent, it will add them to the main group
    PARAMETER:      child        The group which need a parent
    STATE:          finish
    '''

    if debug:
        print "create parent for child:", child.group_id

    group_id = child.group_id[:len(child.group_id) - 1]  # remove the last ID

    if debug:
        print "parents ID:", group_id

    group = search_group(group_id,forceOptimizer)  # check if the group allready exists

    if group is None:  # create a new group if needed
        group = Group(group_id)
        forceOptimizer.groups.append(group)
        if debug:
            print "Parent not exist, create a new Group"

    group.add_child(child)
    child.parent = group

    #check the connection to important pins
    group.connected_gnd = 0
    group.connected_vcc = 0
    group.connected_out = 0
    group.connected_inp = 0

    for c in group.childs:
        group.connected_gnd += c.connected_gnd
        group.connected_vcc += c.connected_vcc
        group.connected_out += c.connected_out
        group.connected_inp += c.connected_inp

    group.connected_parent_east = group.connected_out
    group.connected_parent_south = group.connected_gnd
    group.connected_parent_north = group.connected_vcc

    #if group has parents create them
    if len(group_id) > 1:
        create_parent(group, forceOptimizer, debug)
    #else add group to main group
    else:
        forceOptimizer.group_main.add_child(group)
        group.parent = forceOptimizer.group_main


def find_neighbors(forceOptimizer, debug):
    '''
    DESCRIPTION:    Looking for the neighbors of the groups via pins information of the blocks
    STATE:          not finish
    '''
    if debug:
        print ""
        print "=============="
        print "Find Neighbors"
        print "=============="
        print ""

        print "------"
        print "Step 1"
        print "------"

    # go through all blocks in the circuit
    for block in forceOptimizer.blocks:

        # check all pins in the block
        for pin in block.pins.values():
            # if pin is not connected to a special pin
            if pin.net not in (forceOptimizer.pins_east+forceOptimizer.pins_north+forceOptimizer.pins_south+forceOptimizer.pins_west) and not pin.net.startswith("inp"):
                # add the block to block list in the dictionary
                if pin.net in forceOptimizer.dictionary_net_blocks:
                    if block not in forceOptimizer.dictionary_net_blocks[pin.net]:
                        forceOptimizer.dictionary_net_blocks[pin.net].append(block)
                # if the pin.net_name key does not exists in the dictionary,
                # create a block list with one element
                else:
                    forceOptimizer.dictionary_net_blocks[pin.net] = [block]
    if debug:
        print "------"
        print "Step 2"
        print "------"
    # go over all collected nets
    for key in forceOptimizer.dictionary_net_blocks.keys():

        if key.lower().startswith("vbias"):
            forceOptimizer.bias_nets.add(key.lower())
        # get the list with the blocks connected to the net
        block_list = forceOptimizer.dictionary_net_blocks[key]
        if debug:
            print key, "Count Blocks:", len(block_list)
        # compare the blocks in the list

        for block_1, block_2 in itertools.combinations(block_list, 2):
            if debug:
                print "Block1:", block_1.name, "Block2:", block_2.name
            group_1_id = []
            group_2_id = []

            # start with the high level groups
            for i in range(len(block_1.groups)):
                group_1_id.append(block_1.groups[i])
                group_2_id.append(block_2.groups[i])
                if debug:
                    print "Group1ID:", group_1_id, "Group2ID", group_2_id
                # compare the group IDs and when they are different
                # then connect the groups with each other
                if group_1_id != group_2_id:
                    group_1 = search_group(group_1_id, forceOptimizer)
                    group_2 = search_group(group_2_id, forceOptimizer)

                    # if the groups are already connected, increment the connection number
                    group_1.add_neighbor(group_2, block_1)
                    group_2.add_neighbor(group_1, block_2)
