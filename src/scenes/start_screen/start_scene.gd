extends Control


# TODO: Create an indicator to see on what tab you are on

@export var all_projects: VBoxContainer
@export var new_project_panel: PanelContainer

# For new projects
@export var title_line_edit: LineEdit
@export var path_line_edit: LineEdit
@export var resolution_x_spin_box: SpinBox
@export var resolution_y_spin_box: SpinBox
@export var framerate_spin_box: SpinBox


var open_project_dialog: FileDialog = FileDialog.new()
var choose_path_dialog: FileDialog = FileDialog.new()



func _ready() -> void:
	new_project_panel.visible = false
	title_line_edit.placeholder_text = "Project_%s" % RecentProjectsManager.total_id

	_prepare_dialogs()
	_load_projects()


func _prepare_dialogs() -> void:
	open_project_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	open_project_dialog.access = FileDialog.ACCESS_FILESYSTEM
	open_project_dialog.use_native_dialog = true
	open_project_dialog.filters = ["*.gozen;GoZen project files"]
	if open_project_dialog.file_selected.connect(open_file):
		printerr("Couldn't connect file dialog file_selected!")
	add_child(open_project_dialog)


	choose_path_dialog.file_mode = FileDialog.FILE_MODE_OPEN_DIR
	choose_path_dialog.access = FileDialog.ACCESS_FILESYSTEM
	choose_path_dialog.use_native_dialog = true
	if choose_path_dialog.file_selected.connect(set_new_project_path):
		printerr("Couldn't connect file dialog file_selected!")
	add_child(choose_path_dialog)


func _load_projects() -> void:
	for l_data: RecentProjectData in RecentProjectsManager.get_data():
		var l_project_box: ProjectBox = preload("res://scenes/start_screen/project_box/project_box.tscn").instantiate()
		l_project_box.setup(l_data)
		if l_project_box._on_project_pressed.connect(_on_project_pressed):
			printerr("Couldn't connect _on_project_pressed!")
		all_projects.add_child(l_project_box)


func start_load_scene() -> void:
	if get_tree().change_scene_to_packed(preload("res://scenes/loading_screen/loading_scene.tscn")):
		printerr("Couldn't change scene to loading scene!")


#------------------------------------------------ BUTTONS
func _on_project_pressed(a_id: int) -> void:
	GoZenServer.add_loadables_to_front([
		Loadable.new("Opening project", Project.load_data.bind(RecentProjectsManager.project_data[a_id][0]), 0.3),
		Loadable.new("Setting current project id", RecentProjectsManager.set_current_project_id.bind(a_id)),
	])
	start_load_scene()


func _on_exit_button_pressed() -> void:
	get_tree().quit()


func _on_open_project_button_pressed() -> void:
	open_project_dialog.popup_centered(Vector2i(500,500))


func _on_new_project_button_pressed() -> void:
	new_project_panel.visible = true


func _on_settings_button_pressed() -> void:
	ModuleManager.open_popup(ModuleManager.MENU.SETTINGS)


func _on_support_button_pressed() -> void:
	if OS.shell_open("https://ko-fi.com/voylin"):
		printerr("Something went wrong opening support url!")


func open_file(a_file: String) -> void:
	var l_path: String = a_file.trim_suffix(a_file.split("/")[-1])
	RecentProjectsManager.add_project(l_path, a_file.split("/")[-1].trim_suffix(".gozen"))
	_on_project_pressed(RecentProjectsManager.project_data.size()-1)



#------------------------------------------------ NEW PROJECT BUTTONS
func _on_cancel_create_project_button_pressed() -> void:
	new_project_panel.visible = false


func _on_select_project_path_button_pressed() -> void:
	choose_path_dialog.popup_centered(Vector2i(500,500))


func _on_create_project_button_pressed() -> void:
	var l_title: String = ""
	var l_path: String = ""
	var l_resolution: Vector2i = Vector2i.ZERO
	var l_framerate: int = 30

	if path_line_edit.text == "":
		return

	if title_line_edit.text == "":
		l_title = title_line_edit.placeholder_text
	else:
		l_title = title_line_edit.text

	l_path = path_line_edit.text
	if !l_path.contains(".gozen"):
		if l_path[-1] != "/":
			l_path += "/"
		l_path += "%s.gozen" % l_title.to_lower()
	
	l_resolution.x = resolution_x_spin_box.value as int
	l_resolution.y = resolution_y_spin_box.value as int
	l_framerate = framerate_spin_box.value as int

	RecentProjectsManager.add_project(l_path, l_title)

	Project._project_path = l_path
	Project.title = l_title
	Project.resolution = l_resolution
	Project.framerate = l_framerate

	GoZenServer.add_loadables_to_front([
		Loadable.new("Saving new project", Project.save_data, 0.3),
		Loadable.new("Setting current project id", RecentProjectsManager.set_current_project_id.bind(RecentProjectsManager.project_data.size()-1)),
	])

	start_load_scene()


func set_new_project_path(a_path: String) -> void:
	path_line_edit.text = a_path