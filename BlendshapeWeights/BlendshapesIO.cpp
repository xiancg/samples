#include "BlendshapesIO.h"
#include <fstream>
#include <string>
#include <maya/MFileObject.h>
#include <maya/MGlobal.h>
#include <maya/MStreamUtils.h>


//---------------------------------------------------------
// STATIC CONSTANTS
//---------------------------------------------------------
static const MString WEIGHTS_FILE_EXT = ".bsweights";
static const MString DATA_FILE_EXT = ".bsdata";


//---------------------------------------------------------
// PUBLIC METHODS
//---------------------------------------------------------
BlendshapesIO::BlendshapesIO()
{
}


BlendshapesIO::~BlendshapesIO()
{
}


MStatus BlendshapesIO::write_bs_weights(MString& export_path, BlendshapesData& bs_data, MStringArray& filtered_aliases)
{
	MStatus status;

	std::map<std::string, TargetRange> target_ranges;
	unsigned long long weights_start = 0;
	try
	{
		std::ofstream weights_file(export_path.asChar(), std::ios::binary | std::ios::app);
		for (MString& target_alias : filtered_aliases)
		{
			TargetRange target_range;
			std::vector<VtxIndexWeight> target_weights = bs_data.get_weights_per_target(target_alias);
			target_range.weights_start = weights_start;
			target_range.weights_count = target_weights.size();
			VtxIndexWeight vtx_weight_proxy;
			weights_start = target_range.weights_count + 1;
			for (VtxIndexWeight& vtx_weight : target_weights)
			{
				weights_file.write(reinterpret_cast<char*>(&vtx_weight), sizeof(vtx_weight));
			}
			target_ranges.insert({ target_alias.asChar(), target_range });
		}
		weights_file.close();
	}
	catch (std::ofstream::failure& write_error)
	{
		MString msg;
		msg.format(
			"Error while trying to write to disk '^1s'. Please make sure directory you have the required permissions.\n^2s",
			export_path,
			write_error.what()
		);
		MGlobal::displayError(msg);
	}

	write_bs_data(export_path, bs_data.vertex_count, target_ranges);
	
	return status;
}


MStatus BlendshapesIO::read_bs_weights(
	MString& import_path,
	MStringArray& filtered_aliases,
	std::map<std::string, std::vector<VtxIndexWeight>>& weights_by_target
)
{
	MStatus status;

	std::map<std::string, TargetRange> target_ranges;
	read_bs_data(import_path, target_ranges);
	
	try
	{
		std::ifstream weights_file(import_path.asChar(), std::ios::binary);
		VtxIndexWeight vtx_weight_proxy;
		const unsigned long long size_of_vtx_weight = sizeof(vtx_weight_proxy);
		for (MString& target_alias : filtered_aliases)
		{
			const auto target_range_pair = target_ranges.find(target_alias.asChar());
			if (target_ranges.end() == target_range_pair)
			{
				MString msg;
				msg.format("Target alias ", target_alias, " not found in ", import_path);
				MGlobal::displayInfo(msg);
				MStreamUtils::stdOutStream() << "Transfer: [WARNING] " << "Target alias " << target_alias << " not found in " << import_path << "\n";
				continue;
			}
			const unsigned long long seek_pos = target_range_pair->second.weights_start * size_of_vtx_weight;
			weights_file.seekg(seek_pos);
			std::vector<VtxIndexWeight> vtx_index_weights;
			for (int i = 0; i < target_range_pair->second.weights_count; i++)
			{
				VtxIndexWeight vtx_weight;
				weights_file.read(reinterpret_cast<char*>(&vtx_weight), sizeof(vtx_weight));
				vtx_index_weights.push_back(vtx_weight);
			}
			weights_by_target.insert({ target_alias.asChar(), vtx_index_weights });
		}

		weights_file.close();
	}
	catch (std::ifstream::failure& read_error)
	{
		MString msg;
		msg.format(
			"Error while trying to read from disk '^1s'.\n^2s",
			import_path,
			read_error.what()
		);
		MGlobal::displayError(msg);
	}
	
	return status;
}


MStatus BlendshapesIO::write_bs_data(MString& export_path, unsigned int& vtx_count, std::map<std::string, TargetRange>& target_ranges)
{
	MStatus status;

	MString data_file_path = export_path;
	replace_extension(data_file_path, DATA_FILE_EXT);

	const bool data_file_path_exists = file_exists(data_file_path);

	if (data_file_path_exists)
	{
		std::remove(data_file_path.asChar());
	}

	try
	{
		std::ofstream file(data_file_path.asChar(), std::ios_base::app);
		file << "vtx_count" << "," << vtx_count << std::endl;
		file << "target_alias,weights_start,weights_count" << std::endl;

		for (auto it = target_ranges.begin(); it != target_ranges.end(); ++it)
		{
			std::string target_alias = it->first;
			TargetRange range = it->second;
			file << target_alias << "," << range.weights_start << "," << range.weights_count << std::endl;
		}

		file.close();
	}
	catch (std::ofstream::failure& write_error)
	{
		MString msg;
		msg.format(
			"Error while trying to write to disk '^1s'. Please make sure directory you have the required permissions.\n^2s",
			data_file_path,
			write_error.what()
		);
		MGlobal::displayError(msg);
	}
	
	return status;
}


MStatus BlendshapesIO::read_bs_data(
	MString& import_path,
	std::map<std::string, TargetRange>& target_ranges
)
{
	MStatus status;

	MString data_file_path = import_path;
	replace_extension(data_file_path, DATA_FILE_EXT);

	try
	{
		std::ifstream file(data_file_path.asChar());

		// Vtx count line
		std::string vtx_count_line;
		getline(file, vtx_count_line, '\n');
		// Headers line
		std::string headers;
		getline(file, headers, '\n');
		// Target ranges in bs weights binary file
		std::string alias;
		while(getline(file, alias, ','))
		{
			std::string weights_start;
			std::string weights_count;
			getline(file, weights_start, ',');
			getline(file, weights_count, '\n');
			TargetRange range(std::stoi(weights_start), std::stoi(weights_count));
			target_ranges.insert({alias, range});
		}

		file.close();
	}
	catch (std::ifstream::failure& read_error)
	{
		MString msg;
		msg.format(
			"Error while trying to read from disk '^1s'.\n^2s",
			data_file_path,
			read_error.what()
		);
		MGlobal::displayError(msg);
	}
	
	return status;
}


MStatus BlendshapesIO::read_vtx_count(MString& import_path, unsigned int& vtx_count)
{
	MStatus status;

	MString data_file_path = import_path;
	replace_extension(data_file_path, DATA_FILE_EXT);

	std::ifstream file(data_file_path.asChar());

	std::string vtx_count_title;
	std::string vtx_count_string;
	getline(file, vtx_count_title, ',');
	getline(file, vtx_count_string, ',');

	vtx_count = std::stoi(vtx_count_string);
	
	return status;
}


MString BlendshapesIO::get_weights_extension()
{
	return WEIGHTS_FILE_EXT;
}


MString BlendshapesIO::get_data_extension()
{
	return DATA_FILE_EXT;
}


void BlendshapesIO::format_extension(MString& file_path, const MString& extension)
{
	const unsigned int path_len = file_path.length();
	const int dot_index = file_path.rindex('.');
	if (dot_index == -1)
	{
		file_path += extension;
	}
	else
	{
		const MString path_ext = file_path.substring(dot_index, path_len - 1);
		if (path_ext != extension)
		{
			file_path += extension;
		}
	}
}


void BlendshapesIO::replace_extension(MString& file_path, const MString& extension)
{
	const int dot_index = file_path.rindex('.');
	const MString path_ext = get_extension_from_file_path(file_path);
	if (path_ext != extension)
	{
		MString path_new_extension = file_path.substring(0, dot_index - 1);
		path_new_extension += extension;
		file_path = path_new_extension;
	}
}


bool BlendshapesIO::file_exists(MString& file_path)
{
	MFileObject file_path_obj;
	file_path_obj.setRawFullName(file_path);
	return file_path_obj.exists();
}


bool BlendshapesIO::validate_file_extension(MString& file_path)
{
	const MString path_ext = get_extension_from_file_path(file_path);
	if (path_ext == WEIGHTS_FILE_EXT || path_ext == DATA_FILE_EXT)
	{
		return true;
	}
	return false;
}


MString BlendshapesIO::get_extension_from_file_path(MString& file_path)
{
	const unsigned int path_len = file_path.length();
	const int dot_index = file_path.rindex('.');
	if (dot_index == -1)
	{
		return MString("");
	}
	const MString path_ext = file_path.substring(dot_index, path_len - 1);
	return path_ext;
}
