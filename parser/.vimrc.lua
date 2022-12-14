local dap = require('dap')
path=vim.fn.getcwd() .. '/run.py'
dap.configurations.python = {
  {
    -- The first three options are required by nvim-dap
    type = 'python'; -- the type here established the link to the adapter definition: `dap.adapters.python`
    request = 'launch';
    name = "Launch run.py";

    --[[ options= { ]]
    --[[   env = {}; ]]
    --[[   cwd = "/home/mschroetter/project/cofee_up-repositorys/uebung-1-ringbuffer/"; ]]
    --[[ }; ]]
    -- Options below are for debugpy, see https://github.com/microsoft/debugpy/wiki/Debug-configuration-settings for supported options

    program = path; -- This configuration will launch the current file if used.
    --[[ args = { "--input-dir", "./tmp/scan-build", "--output-junit", "output.xml", "--cf_local", "/home/mschroetter/project/cofee_up/exercises/gbr/0.1/messages.xml", "--cf_global", "/home/mschroetter/project/cofee_up/exercises/gbr/messages.xml", "--srcdir", "/home/mschroetter/ubung-0-stack-live", "--export-errors", "./errors.pkl", "--load-reports", "./reports.plk", "--export-reports", "./reports.plk", "--load-errors", "./errors.pkl", "--create-report", "--output-html", "/tmp" , "--template-dir","/home/mschroetter/project/cofee_up/templates/" }; ]]
    args = { "--input-dir", "/home/mschroetter/project/cofee_up-artifacts/16/results", "--output-junit", "output.xml", "--cf_local", "/home/mschroetter/project/cofee_up/exercises/gbr/2.3/messages.xml", "--cf_global", "/home/mschroetter/project/cofee_up/exercises/gbr/messages.xml", "--srcdir", "/home/mschroetter/project/cofee_up-repositorys/gbr2022/GBR19/uebung-2-prozessliste", "--export-errors", "./errors.pkl", "--create-report", "--output-html", "/tmp/" , "--template-dir","/home/mschroetter/project/cofee_up/templates/" };
    --[[ args = { "--input-dir", "/home/mschroetter/Downloads/cmocka/", "--output-junit", "output.xml", "--cf_local", "/home/mschroetter/project/cofee_up/exercises/gbr/1.5/messages.xml", "--cf_global", "/home/mschroetter/project/cofee_up/exercises/gbr/messages.xml", "--srcdir", "/home/mschroetter/project/cofee_up-repositorys/uebung-1-ringbuffer", "--export-errors", "./errors.pkl", "--export-reports", "./reports.plk", "--create-report", "--output-html", "/tmp" , "--template-dir","/home/mschroetter/project/cofee_up/templates/" }; ]]
    --[[ "--load-errors", "./errors.pkl", "--load-reports", "./reports.plk", ]]
    --
    --[[ pages ]]
    --[[ args = { "--output-html", "/tmp", "--template-dir", "--with-gitlab", "--download-report", "/home/mschroetter/project/cofee_up/templates", "--srcdir", "/home/mschroetter/project/cofee_up-repositorys/uebung-1-ringbuffer", "--load-errors", "/home/mschroetter/Downloads/data", "--create-report",  "--export-report", "./cofee.pkl"}; ]]
    pythonPath = function()
      -- debugpy supports launching an application with a different interpreter then the one used to launch debugpy itself.
      -- The code below looks for a `venv` or `.venv` folder in the current directly and uses the python within.
      -- You could adapt this - to for example use the `VIRTUAL_ENV` environment variable.
      local cwd = vim.fn.getcwd()
      if vim.fn.executable(cwd .. '/venv/bin/python') == 1 then
        return cwd .. '/venv/bin/python'
      elseif vim.fn.executable(cwd .. '/.venv8/bin/python') == 1 then
        return cwd .. '/.venv8/bin/python'
      elseif vim.fn.executable(cwd .. '/.venv/bin/python') == 1 then
        return cwd .. '/.venv/bin/python'
      elseif vim.fn.executable(cwd .. '/.venv/bin/python') == 1 then
        return cwd .. '/.venv/bin/python'
      else
        return '/usr/bin/python'
      end
    end;
  },
}
