#include "LiveDeltasNode.h"

#include <maya/MGlobal.h>
#include <maya/MFnMesh.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnPointArrayData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MItGeometry.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <vector>


//-----------------------------------------------------------------------------
// CONSTANTS
//-----------------------------------------------------------------------------
static const MTypeId TYPE_ID = MTypeId(0x0007F7FC);
static const MString TYPE_NAME = "liveDeltasNode";

//-----------------------------------------------------------------------------
// STATIC VARS
//-----------------------------------------------------------------------------
MObject LiveDeltasNode::base_mesh_obj;
MObject LiveDeltasNode::target_mesh_obj;
MObject LiveDeltasNode::skinned_points_obj;
MObject LiveDeltasNode::skinned_name_obj;
MObject LiveDeltasNode::reverse_obj;


//-----------------------------------------------------------------------------
// PUBLIC METHODS
//-----------------------------------------------------------------------------
LiveDeltasNode::LiveDeltasNode() : MPxDeformerNode() {};

LiveDeltasNode::~LiveDeltasNode() = default;


MStatus LiveDeltasNode::deform(MDataBlock& dataBlock, MItGeometry& geoIter, const MMatrix& matrix, unsigned int multiIndex)
{
    MStatus status;
    float envelope_value = dataBlock.inputValue(envelope).asFloat();
    bool reverse_value = dataBlock.inputValue(reverse_obj).asBool();
    MObject base_mesh = dataBlock.inputValue(base_mesh_obj).asMesh();
    MObject target_mesh = dataBlock.inputValue(target_mesh_obj).asMesh();
    MObject skinned_data_obj = dataBlock.inputValue(skinned_points_obj).data();
    MFnPointArrayData skinned_data_fn(skinned_data_obj, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status)
    MPointArray skinned_points = skinned_data_fn.array(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status)

    if (envelope_value == 0.0f)
    {
        //MGlobal::displayWarning("Skipped deformation, envelope is set to 0.");
		return(MS::kSuccess);
	}

    if (target_mesh.isNull())
    {
        //MGlobal::displayWarning("Skipped deformation, target mesh missing.");
        return(MS::kSuccess);
    }
    if (base_mesh.isNull())
    {
        // MGlobal::displayWarning("Skipped deformation, base mesh is missing.");
        return(MS::kSuccess);
    }
    if (skinned_points.length() == 0)
    {
        // MGlobal::displayWarning("Skipped deformation, skinned mesh is missing.");
        return(MS::kSuccess);
    }

    
    MFnMesh base_mesh_fn(base_mesh, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status)
    MFnMesh target_mesh_fn(target_mesh, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status)

    if (base_mesh_fn.numVertices() != target_mesh_fn.numVertices() || base_mesh_fn.numVertices() != skinned_points.length())
    {
        MGlobal::displayWarning("Skipped deformation, vertex count doesn't match.");
        return(MS::kSuccess);
    }
    
    MPointArray base_points;
    status = base_mesh_fn.getPoints(base_points);
    CHECK_MSTATUS_AND_RETURN_IT(status)
	MPointArray target_points;
	target_mesh_fn.getPoints(target_points);
    CHECK_MSTATUS_AND_RETURN_IT(status)

    float source_weight, final_weight;
    MPoint source_point, delta_vtx, final_vtx;
    geoIter.reset();
    while (!geoIter.isDone())
    {
        // Paintable weights
        source_weight = weightValue(dataBlock, multiIndex, geoIter.index());
        final_weight = source_weight * envelope_value;
        
        source_point = geoIter.position();
        if (reverse_value)
        {
            delta_vtx = (skinned_points[geoIter.index()] + target_points[geoIter.index()]) - base_points[geoIter.index()];
        }else{
            delta_vtx = (target_points[geoIter.index()] - skinned_points[geoIter.index()]) + base_points[geoIter.index()];
        }
        final_vtx = (source_point * (1 - final_weight)) + (delta_vtx * final_weight);
        geoIter.setPosition(final_vtx);

    	geoIter.next();
    }

    return(MS::kSuccess);
}


//-----------------------------------------------------------------------------
// STATIC METHODS
//-----------------------------------------------------------------------------
void* LiveDeltasNode::Creator()
{
    return(new LiveDeltasNode());
}

MStatus LiveDeltasNode::Initialize()
{
    MFnTypedAttribute base_mesh_attr;
    base_mesh_obj = base_mesh_attr.create("baseMesh", "bMesh", MFnData::kMesh);
    MFnTypedAttribute target_mesh_attr;
    target_mesh_obj = target_mesh_attr.create("targetMesh", "tMesh", MFnData::kMesh);
	MFnTypedAttribute skinned_name_attr;
    skinned_name_obj = skinned_name_attr.create("skinnedMeshName", "sMshName", MFnData::kString);
    MFnTypedAttribute skinned_points_attr;
    skinned_points_obj = skinned_points_attr.create("skinnedPoints", "sPoints", MFnData::kPointArray);
    MFnNumericAttribute reverse_attr;
    reverse_obj = reverse_attr.create("reverse", "rev", MFnNumericData::kBoolean, false);

    addAttribute(base_mesh_obj);
    addAttribute(target_mesh_obj);
    addAttribute(skinned_points_obj);
    addAttribute(skinned_name_obj);
    addAttribute(reverse_obj);

    attributeAffects(base_mesh_obj, outputGeom);
    attributeAffects(target_mesh_obj, outputGeom);
    attributeAffects(skinned_points_obj, outputGeom);
    attributeAffects(reverse_obj, outputGeom);

    return(MS::kSuccess);
}

MStatus LiveDeltasNode::setDependentsDirty(const MPlug& in_plug, MPlugArray& affected_plugs)
{
    std::vector<MObject> dirty_objects = {
    	base_mesh_obj,
    	target_mesh_obj,
        skinned_points_obj,
    	reverse_obj
    };
    auto attr_it = std::find(dirty_objects.begin(), dirty_objects.end(), in_plug.attribute());
	if (attr_it != dirty_objects.end())
    {
        MPlug out_array_plug(thisMObject(), outputGeom);
        // Mark the parent output plug as dirty
        affected_plugs.append(out_array_plug);
        // Also visit each element
        const unsigned int n = out_array_plug.numElements();
        for (unsigned int i = 0; i < n; i++)
        {
            MPlug elem_plug = out_array_plug.elementByPhysicalIndex(i);
            affected_plugs.append(elem_plug);
        }
	}

    return(MS::kSuccess);
}

MTypeId LiveDeltasNode::GetTypeId()
{
    return(TYPE_ID);
}

MString LiveDeltasNode::GetTypeName()
{
    return(TYPE_NAME);
}