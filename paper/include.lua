-- Implements: paper/one-source, paper/figures-carry-their-lines, paper/teaser-moves-in-html
-- Pull the paper's text into its skeleton: each ```{.include} block is replaced
-- by the Markdown files it names (one per line, relative to the file holding the
-- block), their own include blocks expanded the same way, and their front matter
-- (the abstract, say) joins the paper's. For LaTeX, a GIF becomes the PNG still
-- stills.py wrote beside it, because LaTeX can't show an animation. Each named
-- figure's caption ends with its two lines, the rebuild and the rerun command,
-- from the figure_lines metadata lines.py wrote, so they're never typed by hand.

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

-- The figure's name if this figure shows a named figure (figures/<name>.<ext>).
local function named(figure)
  local name = nil
  figure.content:walk({
    Image = function(image)
      name = name or image.src:match("^figures/([^/]+)%.%w+$")
    end,
  })
  return name
end

local function with_lines(doc)
  local known = doc.meta.figure_lines or {}
  return doc:walk({
    Figure = function(figure)
      local name = named(figure)
      local two = name and known[name]
      if not two then
        return nil
      end
      local rebuild, rerun = pandoc.utils.stringify(two[1]), pandoc.utils.stringify(two[2])
      local said = pandoc.Inlines({
        pandoc.Space(), pandoc.Str("Remake the figure or replay the game:"), pandoc.Space(), pandoc.Code(rebuild),
        pandoc.Str(";"), pandoc.Space(),
        pandoc.Space(), pandoc.Code(rerun), pandoc.Str("."),
      })
      local long = figure.caption.long
      if #long == 0 then
        long:insert(pandoc.Plain({}))
      end
      long[#long].content:extend(said)
      -- the image's own alt text and caption, the HTML's figcaption, both carry them
      figure.content = figure.content:walk({
        Image = function(image)
          image.caption:extend(said)
          return image
        end,
      })
      return figure
    end,
  })
end

function Pandoc(doc)
  local dir = pandoc.path.directory(PANDOC_STATE.input_files[1])
  doc.blocks = expand(doc.blocks, dir, doc.meta)
  doc = with_lines(doc)
  if FORMAT:match("latex") then
    doc = doc:walk({
      Image = function(image)
        image.src = image.src:gsub("%.gif$", ".png")
        return image
      end,
    })
    -- The PDF can't animate: a GIF teaser shows its `teaser-still` if one is
    -- set, or else the still paper/stills.py writes from its last frame.
    if doc.meta["teaser-still"] then
      doc.meta.teaser = pandoc.utils.stringify(doc.meta["teaser-still"])
    elseif doc.meta.teaser then
      doc.meta.teaser = pandoc.utils.stringify(doc.meta.teaser):gsub("%.gif$", ".png")
    end
  end
  return doc
end
