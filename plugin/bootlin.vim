let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

let g:bootlin_version = get(g:, 'bootlin_version', 'none')

python3 << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
sys.path.insert(0, plugin_root_dir)
import bootlin
EOF

function! BootlinSearchInner(query)
    " New buffer
    new
    " 10 lines high
    resize 10
    " Scratch buffer, don't save
    setlocal buftype=nofile noswapfile nobuflisted nomodified
    " Redirect stdout to bootlinsearch var
    redir => bootlinsearch
    " Actually perform the search, implemented in bootlin.py
    silent python3 bootlin.vim_search()
    " Stop redirecting output
    redir END
    " Move to the top of the buffer
    call cursor(1,1)
    " Put redirected output into the current buffer
    silent put! =bootlinsearch
    " (hack) for some reason there's always an extra line at the beginning, let's delete it
    exe ":1d"
    " Move back to the top of the file
    call cursor(1,1)
    " Remap enter to fetch the source file under the current line
    nmap <buffer> <cr> :silent call BootlinGet()<cr>
    " Don't automatically resize this window when we create the new one
    setlocal noea
    setlocal winfixheight 
endfunction

function! BootlinSearch()
  call inputsave()
  let name = input('bootlin-search: ')
  call inputrestore()
  call BootlinSearchInner(name)
endfunction
command! -nargs=0 Lxs call BootlinSearch()


function! BootlinGet()
    " Grab the current line (that the user pressed enter on)
    let line=getline('.')
    " Create a new split above this one
    above new
    " 20 lines high
    resize 20
    " Make it a scratch buffer
    setlocal buftype=nofile noswapfile nobuflisted nomodified
    " Redirect stdout to bootlinget var
    redir => bootlinget
    " Actually get the source code, implemented in bootlin.py
    silent python3 bootlin.vim_get_source()
    " Stop redirecting output
    redir END
    " Move to the top of the buffer
    call cursor(1,1)
    " Output the source code into this buffer
    silent put! =bootlinget
    " (hack) for some reason there's always an extra line at the beginning, let's delete it
    exe ":1d"
    " Jump to the relevant line number
    call cursor(l:bootlinSearchLineNo, 1)
    " Use C syntax highlighting
    silent set syntax=c
endfunction
