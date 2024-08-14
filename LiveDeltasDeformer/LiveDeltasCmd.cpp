#include "LiveDeltasCmd.h"
#include "LiveDeltasNode.h"
#include "LiveDeltasUtils.h"
#include <algorithm>
#include <fstream>
#include <map>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagModifier.h>
#include <maya/MDagPath.h>
#include <maya/MFnPointArrayData.h>
#include <maya/MGlobal.h>
#include <maya/MPointArray.h>
#include <maya/MSyntax.h>


//---------------------------------------------------------
// CONSTANTS
//---------------------------------------------------------
static const MString MEL_CMD = "liveDeltas";
static const char* NAME_FLAG[2] = { "-n", "-name" };
static const char* REVERSE_FLAG[2] = { "-r", "-reverse" };
static const char* UPDATE_SKIN_DATA_FLAG[2] = { "-usd", "-updateSkinData" };


//---------------------------------------------------------
// STATIC METHODS
//---------------------------------------------------------
void* LiveDeltasCmd::creator()
{
	return(new LiveDeltasCmd());
}

MString LiveDeltasCmd::command_name()
{
	return(MEL_CMD);
}


//---------------------------------------------------------
// PUBLIC METHODS
//---------------------------------------------------------
LiveDeltasCmd::LiveDeltasCmd(){}

LiveDeltasCmd::~LiveDeltasCmd(){}


MStatus LiveDeltasCmd::doIt(const MArgList& args)
{
	MStatus status;
	status = parse_args(args);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	status = redoIt();
	return status;
}


MStatus LiveDeltasCmd::redoIt()
{
	MStatus status;
	if (is_update)
	{
		status = update_live_deltas();
	}
	else
	{
		status = create_live_deltas();

	}
	return status;
}


MStatus LiveDeltasCmd::undoIt()
{
	MStatus status;
	if (!is_update)
	{

		dg_mod.undoIt();

		MDGModifier undo_dg_mod;
		MDagModifier undo_dag_mod;

		status = undo_dg_mod.deleteNode(deltas_node_obj);
		CHECK_MSTATUS_AND_RETURN_IT(status)
		status = undo_dg_mod.doIt();
		CHECK_MSTATUS_AND_RETURN_IT(status)

		status = undo_dag_mod.deleteNode(result_mesh_dag_fn.object());
		CHECK_MSTATUS_AND_RETURN_IT(status)
		status = undo_dag_mod.doIt();
		CHECK_MSTATUS_AND_RETURN_IT(status)
	}
	else
	{
		MGlobal::displayError("Undo is not supported for -updateSkinData mode.");
	
	}

	return status;
}


MStatus LiveDeltasCmd::create_live_deltas()
{
	MStatus status;

	MPointArray skinned_points;
	skinned_mesh_fn.getPoints(skinned_points);

	MObject skinned_mesh_obj = skinned_mesh_fn.object(&status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	MObject intermediate_obj = find_intermediate_object(skinned_mesh_obj);
	if (intermediate_obj.isNull())
	{
		MGlobal::displayError("Failed to find intermediate object for skinned mesh.");
		return MS::kInvalidParameter;
	}
	MFnMesh intermediate_mesh_fn(intermediate_obj, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MFnMesh result_mesh_fn;
	CHECK_MSTATUS_AND_RETURN_IT(status)
	result_mesh_fn.copy(intermediate_obj, MObject::kNullObj, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	result_mesh_fn.setName("result_meshShape", false, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	MObject result_mesh_transform = result_mesh_fn.parent(0);
	status = result_mesh_dag_fn.setObject(result_mesh_transform);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	result_mesh_dag_fn.setName("result_mesh", false, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MStringArray cmd_result;
	MString cmd;
	cmd.format("deformer -type \"liveDeltasNode\" -n \"^1s\" \"^2s\";", node_name, result_mesh_fn.name());
	MGlobal::executeCommand(cmd, cmd_result);
	MSelectionList sel_list;
	sel_list.add(cmd_result[0]);
	status = sel_list.getDependNode(0, deltas_node_obj);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MPlug intermediate_mesh_plug = intermediate_mesh_fn.findPlug("outMesh", false, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	MPlug deltas_base_mesh_plug(deltas_node_obj, LiveDeltasNode::base_mesh_obj);
	status = dg_mod.connect(intermediate_mesh_plug, deltas_base_mesh_plug);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MPlug target_mesh_plug = target_mesh_fn.findPlug("outMesh", false, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	MPlug deltas_target_mesh_plug(deltas_node_obj, LiveDeltasNode::target_mesh_obj);
	status = dg_mod.connect(target_mesh_plug, deltas_target_mesh_plug);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	status = dg_mod.doIt();
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MPlug deltas_skinned_mesh_plug(deltas_node_obj, LiveDeltasNode::skinned_points_obj);
	MFnPointArrayData skinned_points_array_data;
	MObject skinned_obj = skinned_points_array_data.create(skinned_points, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	status = deltas_skinned_mesh_plug.setMObject(skinned_obj);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MPlug deltas_reverse_plug(deltas_node_obj, LiveDeltasNode::reverse_obj);
	status = deltas_reverse_plug.setBool(reverse_delta);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MPlug skinned_mesh_name_plug(deltas_node_obj, LiveDeltasNode::skinned_name_obj);
	MString skinned_name(skinned_mesh_fn.name());
	status = skinned_mesh_name_plug.setString(skinned_name);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	return status;
}


MStatus LiveDeltasCmd::update_live_deltas()
{
	MStatus status;

	MPlug skinned_name_plug(deltas_node_obj, LiveDeltasNode::skinned_name_obj);
	MDataHandle skinned_name_data_handle = skinned_name_plug.asMDataHandle(&status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	MString skinned_mesh_name(skinned_name_data_handle.asString());
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MSelectionList sel_list;
	sel_list.add(skinned_mesh_name);
	MDagPath skinned_dag;
	status = sel_list.getDagPath(0, skinned_dag);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	MFnMesh skinned_mesh_dag_fn(skinned_dag, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	MPointArray skinned_points;
	skinned_mesh_dag_fn.getPoints(skinned_points);

	MPlug deltas_skinned_mesh_plug(deltas_node_obj, LiveDeltasNode::skinned_points_obj);
	MFnPointArrayData skinned_points_array_data;
	MObject skinned_obj = skinned_points_array_data.create(skinned_points, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status)
	status = deltas_skinned_mesh_plug.setMObject(skinned_obj);
	CHECK_MSTATUS_AND_RETURN_IT(status)

	if (has_reverse_flag)
	{
		MPlug deltas_reverse_plug(deltas_node_obj, LiveDeltasNode::reverse_obj);
		status = deltas_reverse_plug.setBool(reverse_delta);
		CHECK_MSTATUS_AND_RETURN_IT(status)
	}

	return MS::kSuccess;
}


MStatus LiveDeltasCmd::parse_args(const MArgList& args)
{
	MStatus status;


	MArgDatabase arg_data(syntax(), args, &status);
	
	if (!status)
	{
		MGlobal::displayError("Error parsing command arguments.");
		return(status);
	}

	if (arg_data.isFlagSet(UPDATE_SKIN_DATA_FLAG[0]))
	{
		arg_data.getFlagArgument(UPDATE_SKIN_DATA_FLAG[0], 0, is_update);
	}

	has_reverse_flag = arg_data.isFlagSet(REVERSE_FLAG[0]);
	if (has_reverse_flag)
	{
		arg_data.getFlagArgument(REVERSE_FLAG[0], 0, reverse_delta);
	}

	has_name_flag = arg_data.isFlagSet(NAME_FLAG[0]);
	if (has_name_flag)
	{
		arg_data.getFlagArgument(NAME_FLAG[0], 0, node_name);
	}

	MSelectionList sel_list;
	status = arg_data.getObjects(sel_list);
	if (!status)
	{
		MGlobal::displayError("Failed to get selection list");
		return(status);
	}

	unsigned int num_objects = 2;
	if (is_update)
	{
		num_objects = 1;
	}
	if (sel_list.length() != num_objects and is_update)
	{
		MGlobal::displayError("LiveDeltas -updateSkinData mode requires the name of a LiveDeltasNode.");
		return(MS::kInvalidParameter);
	}
	if (sel_list.length() != num_objects and !is_update)
	{
		MGlobal::displayError("LiveDeltas command requires two objects to be passed or selected.");
		return(MS::kInvalidParameter);
	}
	
	if (!is_update)
	{
		MDagPath skinned_dag;
		MDagPath target_dag;
		status = sel_list.getDagPath(0, skinned_dag);
		CHECK_MSTATUS_AND_RETURN_IT(status)
		status = sel_list.getDagPath(1, target_dag);
		CHECK_MSTATUS_AND_RETURN_IT(status)
		status = skinned_mesh_fn.setObject(skinned_dag);
		CHECK_MSTATUS_AND_RETURN_IT(status)
		status = target_mesh_fn.setObject(target_dag);
		CHECK_MSTATUS_AND_RETURN_IT(status)
	}
	else
	{
		status = sel_list.getDependNode(0, deltas_node_obj);
		CHECK_MSTATUS_AND_RETURN_IT(status)
	}

	return status;
}


MSyntax LiveDeltasCmd::create_syntax()
{
	MSyntax syntax;

	MStatus status = syntax.addFlag(REVERSE_FLAG[0], REVERSE_FLAG[1], MSyntax::kBoolean);
	check_flag_status(REVERSE_FLAG[1], status);
	status = syntax.addFlag(UPDATE_SKIN_DATA_FLAG[0], UPDATE_SKIN_DATA_FLAG[1], MSyntax::kBoolean);
	check_flag_status(UPDATE_SKIN_DATA_FLAG[1], status);
	status = syntax.addFlag(NAME_FLAG[0], NAME_FLAG[1], MSyntax::kString);
	check_flag_status(NAME_FLAG[1], status);

	syntax.setObjectType(MSyntax::kSelectionList, 1, 2);

	syntax.enableEdit(false);
	syntax.enableQuery(false);

	return syntax;
}


void LiveDeltasCmd::check_flag_status(const char* flag_name, MStatus& status)
{
	if (!status)
	{
		MString msg;
		msg.format("Couldn't add flag ^1s to ^2s command.", MString(flag_name), command_name());
		MGlobal::displayError(msg);
	}
}


bool LiveDeltasCmd::isUndoable() const
{
	return true;
}
