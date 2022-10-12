# Recursive function that formats a list of objects that describe
# environment variables into an explanatory string:
# [{Var = "python3.10"; Source = "PROCESS"}, {Var = "python3.8"; Source = "USER"}, {Var = "python2.7"; Source = "MACHINE"}]
# becomes
# "python3.10 (overrides python3.8 from USER) (overrides python2.7 from MACHINE)"
function Format-Vars ($CurrentString, $ListOfVars) {
    if ( $ListOfVars.Count -eq 0 ) {
        return $CurrentString
    }
    $Var = $ListOfVars[0]
    if ( !$CurrentString ) {
        $CurrentString = $Var.Value
    }
    else {
        $Value = $Var.Value
        $Source = $Var.Source
        $CurrentString += " (overrides $Value from $Source)"
    }
    return Format-Vars -CurrentString $CurrentString -ListOfVars $ListOfVars.GetRange(1, $ListOfVars.Count - 1)
}

# Removes duplicate values from a list of objects, keeping the first occurrence
# this filters out variables where the value is the same but the source is different,
# ie. the user has set his PATH to the same value as the system: the system path is no
# longer relevant
function Remove-Duplicates ($List) {
    $Prev = $null
    $NewList = [System.Collections.ArrayList]::new()

    foreach ( $Var in $List ) {
        if ($Prev -and $Var.Value -eq $Prev.Value) {
            continue
        }

        $NewList.Add($Var)
        $Prev = $Var
    }

    return (, $NewList)
}

# Shows the environment variables for the currently running process
# highlighting the ones that are different from the user and machine defaults
# Example:
# PS > Import-Module .\explain_env.ps1
# PS > $env:TEMP = "/tmp" # set variable for process
# PS > Show-Env TEMP
# TEMP = /tmp (overrides C:\Users\user\AppData\Local\Temp from USER) (overrides C:\WINDOWS\TEMP from MACHINE)
function Show-Env ($SpecificVar) {
    $Explained = @{}
    $Process = [System.Environment]::GetEnvironmentVariables('Process')
    $User = [System.Environment]::GetEnvironmentVariables('User')
    $Machine = [System.Environment]::GetEnvironmentVariables('Machine')

    foreach ( $var in $Process.GetEnumerator() ) {
        if ( !$Explained.ContainsKey($var.Name) ) {
            $Explained.Add($var.Name, [System.Collections.ArrayList]::new())
        }
        $null = $Explained[$var.Name].Add([PSCustomObject]@{
                Value  = $var.Value;
                Source = 'Process';
            })
    }
    foreach ( $var in $User.GetEnumerator() ) {
        if ( !$Explained.ContainsKey($var.Name) ) {
            $Explained.Add($var.Name, [System.Collections.ArrayList]::new())
        }
        $null = $Explained[$var.Name].Add([PSCustomObject]@{
                Value  = $var.Value;
                Source = 'User';
            })
    }
    foreach ( $var in $Machine.GetEnumerator() ) {
        if ( !$Explained.ContainsKey($var.Name) ) {
            $Explained.Add($var.Name, [System.Collections.ArrayList]::new())
        }
        $null = $Explained[$var.Name].Add([PSCustomObject]@{
                Value  = $var.Value;
                Source = 'Machine';
            })
    }

    if ($SpecificVar) {
        if ( !$Explained.ContainsKey($SpecificVar) ) {
            Write-Host "Variable $SpecificVar not found"
            return
        }
        $Name = $SpecificVar
        $Values = Remove-Duplicates -List $Explained[$SpecificVar]
        $Value = Format-Vars -CurrentString $null -ListOfVars $Values[$Values.Count - 1]
        Write-Host "$Name`: $Value"
    }
    else {
        foreach ( $var in $Explained.GetEnumerator()) {
            $Name = $var.Name
            $Values = Remove-Duplicates -List $var.Value
            $Value = Format-Vars -CurrentString $null -ListOfVars $Values[$Values.Count - 1]
            Write-Host "$Name`: $Value"
        }
    }
}

