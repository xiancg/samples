#include "RigManipulatorCtx.h"
#include "RigManipulatorMoveToolCmd.h"

#include <maya/MColor.h>
#include <maya/MCursor.h>
#include <maya/MDagPath.h>
#include <maya/MEvent.h>
#include <maya/MFnTransform.h>
#include <maya/MFrameContext.h>
#include <maya/MItSelectionList.h>
#include <maya/MString.h>
#include <maya/MUIDrawManager.h>
#include <maya/MVector.h>



//---------------------------------------------------------------------------
// STATIC CONSTANTS
//---------------------------------------------------------------------------
static const MString CTX_TITLE = "Rig Manipulator";
static const MString GENERAL_HELP_TEXT = "Left click to SELECT and MOVE. Middle click to MOVE.";

//---------------------------------------------------------------------------
// PUBLIC METHODS
//---------------------------------------------------------------------------
RigManipulatorCtx::RigManipulatorCtx()
{
	setTitleString(CTX_TITLE);
	sensitivity_values["control"] = 0.5;
	sensitivity_values["shift"] = 1.5;
	sensitivity_values["default"] = 1.0;
	view = M3dView::active3dView();
}


MStatus RigManipulatorCtx::helpStateHasChanged(MEvent &event)
{
	MStatus status = setHelpString(GENERAL_HELP_TEXT);
	return(status);
}


void RigManipulatorCtx::toolOnSetup(MEvent& event)
{
	const MString str(GENERAL_HELP_TEXT);
	setHelpString(str);
}


MStatus RigManipulatorCtx::doPress(MEvent &event, MHWRender::MUIDrawManager &draw_mgr, const MHWRender::MFrameContext &context)
{
	MStatus status;
	update_keyboard_modifiers(event);
	update_sensitivity();
	view = M3dView::active3dView();
	setCursor(MCursor::crossHairCursor);
	event.getPosition(viewport_start_pos_x, viewport_start_pos_y);
	if (event.mouseButton() == MEvent::kLeftMouse)
	{
		event.getPosition(viewport_end_pos_x, viewport_end_pos_y);
		if(hit_test())
		{
			control_clicked = true;
			MGlobal::getActiveSelectionList(move_selection);
			if (!move_selection.isEmpty())
			{
				mirror_options(move_selection);
				move_tool_cmd = static_cast<RigManipulatorMoveToolCmd*>(newToolCommand());
				move_tool_cmd->init_attributes(move_selection);
			}
		}
		else
		{
			control_clicked = false;
		}
		
	}
	else if(event.mouseButton() == MEvent::kMiddleMouse)
	{
		MGlobal::getActiveSelectionList(move_selection);
		mirror_options(move_selection);
		// Create an instance of the move tool command.
		move_tool_cmd = static_cast<RigManipulatorMoveToolCmd*>(newToolCommand());
		move_tool_cmd->init_attributes(move_selection);
	}
	return(status);
}


MStatus RigManipulatorCtx::doDrag(MEvent &event, MHWRender::MUIDrawManager &draw_mgr, const MHWRender::MFrameContext &context)
{
	MStatus status;
	update_keyboard_modifiers(event);
	update_sensitivity();
	event.getPosition(viewport_end_pos_x, viewport_end_pos_y);
	if (event.mouseButton() == MEvent::kLeftMouse)
	{
		if (!move_selection.isEmpty() && control_clicked)
		{
			status = move_behaviour(event);
			CHECK_MSTATUS_AND_RETURN_IT(status)
			move_drag = true;
		}
		else
		{
			SelectionRectangle selection_rect;
			selection_rect.upper_left.x = viewport_start_pos_x;
			selection_rect.upper_left.y = viewport_start_pos_y;
			selection_rect.upper_right.x = viewport_end_pos_x;
			selection_rect.upper_right.y = viewport_start_pos_y;
			selection_rect.bottom_right.x = viewport_end_pos_x;
			selection_rect.bottom_right.y = viewport_end_pos_y;
			selection_rect.bottom_left.x = viewport_start_pos_x;
			selection_rect.bottom_left.y = viewport_end_pos_y;
			
			draw_selection_rect(
				draw_mgr,
				selection_rect
			);
			move_drag = false;
		}
	}
	else if (event.mouseButton() == MEvent::kMiddleMouse)
	{
		if(!move_selection.isEmpty())
		{
			status = move_behaviour(event);
			CHECK_MSTATUS_AND_RETURN_IT(status)
		}
	}
	return(status);
}


MStatus RigManipulatorCtx::doRelease(MEvent &event, MHWRender::MUIDrawManager &draw_mgr, const MHWRender::MFrameContext &context)
{
	MStatus status;
	//Refresh end pos here for click-pick selection
	event.getPosition(viewport_end_pos_x, viewport_end_pos_y);
	if (event.mouseButton() == MEvent::kLeftMouse)
	{
		if(move_drag)
		{
			cleanup_tool_cmd();
		}
		else
		{
			make_selection();
		}
	}
	else if (event.mouseButton() == MEvent::kMiddleMouse)
	{
		if (!move_selection.isEmpty())
		{
			cleanup_tool_cmd();
		}
	}
	view.refresh(true);
	move_drag = false;
	setCursor(MCursor::defaultCursor);
	return(status);
}


MStatus RigManipulatorCtx::cleanup_tool_cmd()
{
	MStatus status;
	/*
	Delete the move command if we have moved less then 2 pixels
	otherwise call finalize to set up the journal and add the
	command to the undo queue.
	*/
	int moved_x = viewport_end_pos_x - viewport_start_pos_x;
	int moved_y = viewport_end_pos_y - viewport_start_pos_y;
	if (abs(moved_x) < 2 && abs(moved_y) < 2)
	{
		delete move_tool_cmd;
	}
	else
	{
		status = move_tool_cmd->finalize();
	}
	return(status);
}


void RigManipulatorCtx::update_keyboard_modifiers(MEvent& event)
{
	control_mod = event.isModifierControl();
	shift_mod = event.isModifierShift();
}


void RigManipulatorCtx::update_sensitivity()
{
	if(control_mod && !shift_mod)
	{
		sensitivity = sensitivity_values["control"];
	}
	else if (shift_mod && !control_mod)
	{
		sensitivity = sensitivity_values["shift"];
	}
	else
	{
		sensitivity = sensitivity_values["default"];
	}
}


void RigManipulatorCtx::draw_selection_rect(MHWRender::MUIDrawManager &draw_mgr, SelectionRectangle& selection_rect)
{
	draw_mgr.beginDrawable();

	draw_mgr.setLineWidth(1.0);
	draw_mgr.setColor(MColor(1.0, 1.0, 1.0));

	draw_mgr.line2d(selection_rect.upper_left, selection_rect.upper_right);
	draw_mgr.line2d(selection_rect.upper_right, selection_rect.bottom_right);
	draw_mgr.line2d(selection_rect.bottom_right, selection_rect.bottom_left);
	draw_mgr.line2d(selection_rect.bottom_left, selection_rect.upper_left);

	draw_mgr.endDrawable();
}


MStatus RigManipulatorCtx::move_behaviour(MEvent &event)
{
	MStatus status;

	short end_pos_x;
	short end_pos_y;
	event.getPosition(end_pos_x, end_pos_y);

	move_tool_cmd->undoIt();
	MouseDragPoints drag_points = {viewport_start_pos_x, viewport_start_pos_y, end_pos_x, end_pos_y};
	move_tool_cmd->set_initial_move_vector(drag_points,sensitivity);
	move_tool_cmd->redoIt();

	view.refresh(true);

	return(status);
}


bool RigManipulatorCtx::hit_test()
{
	MSelectionList initial_selection;
	MGlobal::getActiveSelectionList(initial_selection);
	
	MGlobal::selectFromScreen(
		viewport_end_pos_x, viewport_end_pos_y,
		MGlobal::kReplaceList
	);
	MSelectionList selection_list;
	MGlobal::getActiveSelectionList(selection_list);
	filter_controls_only(selection_list);
	selection_list.intersect(initial_selection);

	MGlobal::setActiveSelectionList(initial_selection, MGlobal::kReplaceList);
	
	if(selection_list.isEmpty())
	{
		return false;
	}
	return true;
}


void RigManipulatorCtx::make_selection()
{
	MSelectionList initial_selection;
	MSelectionList mod_selection;
	MGlobal::getActiveSelectionList(initial_selection);
	MGlobal::getActiveSelectionList(mod_selection);
	int x_delta = abs(viewport_end_pos_x - viewport_start_pos_x);
	int y_delta = abs(viewport_end_pos_y - viewport_start_pos_y);
	if (x_delta < 2 && y_delta < 2)
	{
		//If no drag action, click-pick type selection is made
		MGlobal::selectFromScreen(
			viewport_end_pos_x, viewport_end_pos_y,
			MGlobal::kReplaceList
		);
	}
	else
	{
		MGlobal::selectFromScreen(
			viewport_start_pos_x, viewport_start_pos_y,
			viewport_end_pos_x, viewport_end_pos_y,
			MGlobal::kReplaceList
		);
	}
	MSelectionList selection_list;
	MGlobal::getActiveSelectionList(selection_list);

	if (control_mod && shift_mod)
	{
		mod_selection.merge(selection_list, MSelectionList::kMergeNormal);
	}
	else if(shift_mod && !control_mod)
	{
		mod_selection.merge(selection_list, MSelectionList::kXORWithList);
	}
	else if(control_mod && !shift_mod)
	{
		mod_selection.merge(selection_list, MSelectionList::kRemoveFromList);
	}
	else
	{
		mod_selection = selection_list;
	}

	mirror_options(mod_selection);

	MGlobal::setActiveSelectionList(initial_selection, MGlobal::kReplaceList);
	MGlobal::selectCommand(mod_selection, MGlobal::kReplaceList);
}


void RigManipulatorCtx::mirror_options(MSelectionList &selection_list)
{
	if (!selection_list.isEmpty())
	{
		filter_controls_only(selection_list);
		if (!selection_list.isEmpty())
		{
			//Shortcut: If Ctrl+Shift is pressed, select the mirrored control
			bool current_horizontal_mirror = horizontal_mirror;
			bool current_vertical_mirror = vertical_mirror;
			if (control_mod && shift_mod)
			{
				horizontal_mirror = true;
			}
			if (horizontal_mirror || vertical_mirror)
			{
				mirror_selection(selection_list);
			}
			horizontal_mirror = current_horizontal_mirror;
			vertical_mirror = current_vertical_mirror;
		}
	}
}


void RigManipulatorCtx::filter_controls_only(MSelectionList &selection_list)
{
	MStringArray selection_strings;
	selection_list.getSelectionStrings(selection_strings);
	for (int i = selection_list.length() - 1; i >= 0; i--)
	{
		MString path_name = selection_strings[i];
		if (path_name.index('|') != -1)
		{
			MStringArray splitted;
			path_name.split('|', splitted);
			path_name = splitted[splitted.length() - 1];
		}
		if (filter_objects.indexOf(path_name) == -1)
		{
			selection_list.remove(i);
		}
	}
}
