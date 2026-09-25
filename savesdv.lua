-- SaveSDV Lua companion / CLI editor.
-- The desktop GUI lives in the Python clients. This Lua tool keeps the core workflow usable from Lua.
-- Usage: lua savesdv.lua <save-file> [player-name] [farm-name] [money]

local save_path = arg[1]
if not save_path then
    io.stderr:write("Usage: lua savesdv.lua <save-file> [player-name] [farm-name] [money]\n")
    os.exit(1)
end

local function read_all(path)
    local f = assert(io.open(path, "rb")); local data = f:read("*a"); f:close(); return data
end

local function write_all(path, data)
    local f = assert(io.open(path, "wb")); f:write(data); f:close()
end

local function xml_escape(s)
    s = tostring(s or "")
    s = s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;")
    s = s:gsub('"', "&quot;"):gsub("'", "&apos;")
    return s
end

local xml = read_all(save_path)
if not xml:find("<player>") and not xml:find("<player%s") then
    io.stderr:write("SaveSDV: could not find <player> in the selected save.\n")
    os.exit(1)
end

local backup = save_path .. "." .. os.date("%Y%m%d_%H%M%S") .. ".bak"
write_all(backup, xml)

local function replace_field(text, field, value)
    local pattern = "(<" .. field .. ">)(.-)(</" .. field .. ">)"
    local replaced, count = text:gsub(pattern, "%1" .. xml_escape(value) .. "%3", 1)
    if count == 0 then
        io.stderr:write("SaveSDV: could not find <" .. field .. ">.\n")
        os.exit(1)
    end
    return replaced
end

if arg[2] then xml = replace_field(xml, "name", arg[2]) end
if arg[3] then xml = replace_field(xml, "farmName", arg[3]) end
if arg[4] then
    local number = tonumber(arg[4])
    if not number then io.stderr:write("SaveSDV: money must be a number.\n"); os.exit(1) end
    xml = replace_field(xml, "money", tostring(math.floor(number)))
end

write_all(save_path, xml)
local lower = xml:lower()
if lower:find("moddata", 1, true) or lower:find("smapi", 1, true) then
    io.write("WARNING: mods were detected in the save. SaveSDV does not fully support mods.\n")
end
io.write("Save updated successfully.\nBackup: " .. backup .. "\n")
