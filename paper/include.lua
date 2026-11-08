-- Implements: paper/one-source
-- Pull the paper's text into its skeleton: each ```{.include} block is replaced
-- by the Markdown files it names (one per line, relative to the file holding the
-- block), their own include blocks expanded the same way, and their front matter
-- (the abstract, say) joins the paper's. For LaTeX, a GIF becomes the PNG still
-- stills.py wrote beside it, because LaTeX can't show an animation.

local function expand(blocks, dir, meta)
  local out = pandoc.List()
  for _, block in ipairs(blocks) do
    if block.t == "CodeBlock" and block.classes:includes("include") then
      for name in block.text:gmatch("[^\n]+") do
        local path = pandoc.path.join({ dir, name })
        local file = assert(io.open(path), "paper: can't open " .. path)
        local part = pandoc.read(file:read("a"), "markdown", PANDOC_READER_OPTIONS)
        file:close()
        out:extend(expand(part.blocks, pandoc.path.directory(path), meta))
        for key, value in pairs(part.meta) do
          if meta[key] == nil then
            meta[key] = value
          end
        end
      end
    else
      out:insert(block)
    end
  end
  return out
end

function Pandoc(doc)
  local dir = pandoc.path.directory(PANDOC_STATE.input_files[1])
  doc.blocks = expand(doc.blocks, dir, doc.meta)
  if FORMAT:match("latex") then
    doc = doc:walk({
      Image = function(image)
        image.src = image.src:gsub("%.gif$", ".png")
        return image
      end,
    })
    if doc.meta.teaser then
      doc.meta.teaser = pandoc.utils.stringify(doc.meta.teaser):gsub("%.gif$", ".png")
    end
  end
  return doc
end
