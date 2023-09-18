"""
Previous version of this is upscaling on households and is problematic because its impossible to calculate new household IDs

Get household IDs
shuffle IDs using hashing mod 10**20 to give 20 digit IDs

for each new households ID
get everyone with the old household ID
assign them the new household ID
put them into the population

Probably some fancy way to do this pandas gruoping/merger.
left (right?) merge on hidp might be the simplest way to do this?

"""

