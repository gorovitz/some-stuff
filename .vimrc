" Use Vim settings, rather than Vi settings (much better!).
" This must be first, because it changes other options as a side effect.
set nocompatible

" options for omnifunc
set nocp
filetype plugin on
"OmniComplit
" map <C-F12> :!ctags -R --c++-kinds=+p --fields=+iaS --extra=+q .<CR>
" set GlobalSearch for omni
" let OmniCpp_GlobalScopeSearch = 1
" search namespaces in cur. buffer and in included files (default - 1)
" let OmniCpp_NamespaceSearch = 2

"basic instructions
" Формат строки состояния
set statusline=%<%f%h%m%r\ %b\ %{&encoding}\ 0x\ \ %l,%c%V\ %P 
set laststatus=2

" Опции сесссий
set sessionoptions=curdir,buffers,tabpages

"-------------------------
" Горячие клавишы
"-------------------------

" Пробел в нормальном режиме перелистывает страницы
nmap <Space> <PageDown>

" F5 - просмотр списка буферов
nmap <F5> <Esc>:BufExplorer<cr>
vmap <F5> <esc>:BufExplorer<cr>
imap <F5> <esc><esc>:BufExplorer<cr>

" F6 - предыдущий буфер
map <F6> :bp<cr>
vmap <F6> <esc>:bp<cr>i
imap <F6> <esc>:bp<cr>i

" F7 - следующий буфер
map <F7> :bn<cr>
vmap <F7> <esc>:bn<cr>i
imap <F7> <esc>:bn<cr>i

"ClangComplete
" if some options not working set this variable
let g:clang_user_options='|| exit 0'
let g:clang_use_library=1
let g:clang_complete_copen=1
let g:clang_complete_macros=1
let g:clang_complete_patterns=0
let g:clang_auto_select=1

" resize horzontal split window
nmap <c-Left> <c-w>-<c-w>-
nmap <c-Right> <c-w>+<c-w>+
" resize vertical split window
nmap <c-Up> <c-w>><c-w>>
nmap <c-Down> <c-w><<c-w><

filetype plugin indent on
"syntax on

call pathogen#runtime_append_all_bundles()
call pathogen#helptags()

"backup settings"
set backupdir=./.backup,.,/tmp
set directory=.,./.backup,/tmp

"set background=dark
colorscheme desert
"set background=light
" allow copy/paste to clipboard
set clipboard=unnamedplus

"disable auto commenting for lower lines after the comment
autocmd FileType * setlocal formatoptions-=c formatoptions-=r formatoptions-=o

"<leader>pw when our cursor is on a module and have a new window open with the
"whole documentation page for it.
au FileType python set omnifunc=pythoncomplete#Complete
let g:SuperTabDefaultCompletionType = "context"
set completeopt=menuone,longest,preview

"For Gundo - revision plugin
map <leader>g :GundoToggle<CR>
"Ack finder - like grep
nmap <leader>a <Esc>:Ack!

let mapleader = ","
let g:tagbar_usearrows = 1

nnoremap <leader>tg :TagbarToggle<CR>

map <leader>n :NERDTreeToggle<CR>
map <leader>j :RopeGotoDefinition<CR>
map <leader>r :RopeRename<CR>
" Execute the tests
nmap <silent><Leader>tf <Esc>:Pytest file<CR>
nmap <silent><Leader>tc <Esc>:Pytest class<CR>
nmap <silent><Leader>tm <Esc>:Pytest method<CR>
" cycle through test errors
nmap <silent><Leader>tn <Esc>:Pytest next<CR>
nmap <silent><Leader>tp <Esc>:Pytest previous<CR>
nmap <silent><Leader>te <Esc>:Pytest error<CR>

"Virtualenv
" Add the virtualenv's site-packages to vim path
py << EOF
import os.path
import sys
import vim
if 'VIRTUAL_ENV' in os.environ:
    project_base_dir = os.environ['VIRTUAL_ENV']
    sys.path.insert(0, project_base_dir)
    activate_this = os.path.join(project_base_dir, 'bin/activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))
EOF

"<leader>pw when our cursor is on a module and have a new window open with the
"whole documentation page for it.
map <leader>td <Plug>TaskList

"Change path to look for pydoc:
"let g:pydoc_cmd = '/usr/bin/epydoc'
" or 
"let g:pydoc_cmd = 'python2 -m epydoc'

syntax on                           " syntax highlighing
filetype on                          " try to detect filetypes
filetype plugin indent on    " enable loading indent file for filetype

let g:pyflakes_use_quickfix = 0
let g:pep8_map='<leader>8'


"already in some plugins
"set foldmethod=indent

set foldlevel=99

"to move around a windows (not using a Ctrl + w + <movement>
map <c-j> <c-w>j
map <c-k> <c-w>k
map <c-l> <c-w>l
map <c-h> <c-w>h


" When started as "evim", evim.vim will already have done these settings.
if v:progname =~? "evim"
  finish
endif


" allow backspacing over everything in insert mode
set backspace=indent,eol,start

if has("vms")
  set nobackup          " do not keep a backup file, use versions instead
else
  set backup            " keep a backup file
endif
set history=50          " keep 50 lines of command line history
set ruler               " show the cursor position all the time
set showcmd             " display incomplete commands
set incsearch           " do incremental searching

" For Win32 GUI: remove 't' flag from 'guioptions': no tearoff menu entries
" let &guioptions = substitute(&guioptions, "t", "", "g")

" Don't use Ex mode, use Q for formatting
map Q gq


" CTRL-U in insert mode deletes a lot.  Use CTRL-G u to first break undo,
" so that you can undo CTRL-U after inserting a line break.
inoremap <C-U> <C-G>u<C-U>

" In many terminal emulators the mouse works just fine, thus enable it.
if has('mouse')
  set mouse=a
endif

" Switch syntax highlighting on, when the terminal has colors
" Also switch on highlighting the last used search pattern.
if &t_Co > 2 || has("gui_running")
  syntax on
  set hlsearch
endif

" Only do this part when compiled with support for autocommands.
if has("autocmd")

  " Enable file type detection.
  " Use the default filetype settings, so that mail gets 'tw' set to 72,
  " 'cindent' is on in C files, etc.
  " Also load indent files, to automatically do language-dependent indenting.
  filetype plugin indent on

  " Put these in an autocmd group, so that we can delete them easily.
  augroup vimrcEx
  au!

  " For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78

  " When editing a file, always jump to the last known cursor position.
  " Don't do it when the position is invalid or when inside an event handler
  " (happens when dropping a file on gvim).
  " Also don't do it when the mark is in the first line, that is the default
  " position when opening a file.
  autocmd BufReadPost *
    \ if line("'\"") > 1 && line("'\"") <= line("$") |
    \   exe "normal! g`\"" |
    \ endif

  augroup END

else

  set autoindent                " always set autoindenting on
endif " has("autocmd")

" Convenient command to see the difference between the current buffer and the
" file it was loaded from, thus the changes you made.
" Only define it when not defined already.
if !exists(":DiffOrig")
  command DiffOrig vert new | set bt=nofile | r ++edit # | 0d_ | diffthis
                  \ | wincmd p | diffthis
endif




function! Find(name)
  let l:list=system("find . -name '".a:name."' | perl -ne 'print \"$.\\t$_\"' ")
  let l:num=strlen(substitute(l:list, "[^\n]", "", "g"))
  if l:num < 1
    echo "'".a:name."' not found"
    return
  endif
  if l:num != 1
    echo l:list
    let l:input=input("Which ? (CR=nothing)\n")
    if strlen(l:input)==0
      return
    endif
    if strlen(substitute(l:input, "[0-9]", "", "g"))>0
      echo "Not a number"
      return
    endif
    if l:input<1 || l:input>l:num
      echo "Out of range"
      return
    endif
    let l:line=matchstr("\n".l:list, "\n".l:input."\t[^\n]*")
  else
    let l:line=l:list
  endif
  let l:line=substitute(l:line, "^[^\t]*\t./", "", "")
  execute ":e ".l:line
endfunction
command! -nargs=1 Find :call Find("<args>")

function! DoMklocal()
    let l:goback = printf(":cd %s", getcwd())
    echo strpart(expand("%"), 0, 5)
    if strpart(expand("%"), 0, 5) == "dhcp3"
        echo "DHCP!"
    endi
    execute ":cd %:h"
    execute ":!mklocal"
    execute l:goback
    " call system("sudo cp $IB/src/test.py $CHR")
endfunction
nmap <F7> :call DoMklocal()<CR>
nmap ;m :call DoMklocal()<CR>


set expandtab
set tabstop=4
set list
set listchars=trail:.,tab:>> 
set nu
set cpt-=i
set cscopetag


function! GotoXml(structname)
    if a:structname == "none"
        let l:str = getline(".")
        let l:template = '[\x27\."?]\(\(\l\+\)\.\([a-z_46]\+\)\)[\x27 "]'
        let l:mlist = matchlist(l:str, l:template, getpos(".")[2])
        echo l:mlist
        if len(l:mlist) != 0
            let l:mlist = matchlist(l:str, l:template)
            echo l:mlist
            let l:type = l:mlist[3]
            let l:pkg = l:mlist[2]
        else
            echo("Don't see any type declaration in current string")
            return
        endif
    else
        echo a:structname
        let l:mlist = split(a:structname, "\\.")
        let l:type = l:mlist[1]
        let l:pkg = l:mlist[0]
        echo l:mlist
    endif
    let l:cmd = printf('grep -nr "structure name=\"%s\"" $SRC/products/%s/xml/', l:type, l:pkg)
    let l:fnamestr = system(l:cmd)
    if len(l:fnamestr) != 0 && v:shell_error == 0
        let l:mlist = matchlist(l:fnamestr, '\(\S\+\):\(\d\+\):')
        let l:fname = mlist[1]
        let l:fpos = mlist[2]
        if filereadable(l:fname)
            execute ":e +".l:fpos." ".l:fname
        else
            echo printf("File %s not found", l:fname)
        endif
    else
        echo printf("Structure %s not found in package %s", l:type, l:pkg)
    endif
endfunction
command! -nargs=1 GotoXml :call GotoXml("<args>")
nmap ;x   :call GotoXml("none")<CR><CR>
