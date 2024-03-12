let prev_folder;

function start() {
    let i;

    const toggler = document.getElementsByClassName("caret");
    for (i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", toggleTree, false);
    }

    const files = document.getElementsByClassName("file");
    for (i = 0; i < files.length; i++) {
        files[i].addEventListener("click", getFile, false);
    }

    document.getElementById("menu_file").addEventListener("click", menuDisable, false);
    document.getElementById("add_root_folder").addEventListener("click", addRootFolder, false);
    document.getElementById("add_subfolder").addEventListener("click", addSubfolder, false);
    document.getElementById("delete_folder").addEventListener("click", deleteFolder, false);
    document.getElementById("add_file").addEventListener("click", addFile, false);
    document.getElementById("delete_file").addEventListener("click", deleteFile, false);
    
    document.getElementById("menu_code").addEventListener("click", menuDisable, false);
    document.getElementById("split").addEventListener("click", runSplitter, false);
    document.getElementById("create_section").addEventListener("click", createSection, false);
    document.getElementById("compile").addEventListener("click", submitCompile, false);
    document.getElementById("delete_section").addEventListener("click", deleteSection, false);

    document.getElementById("menu_asm").addEventListener("click", menuDisable, false);
    document.getElementById("download_asm").addEventListener("click", runDownloader, false);
    document.getElementById("hide_asm_body").addEventListener("click", hideAsmBody, false);
    document.getElementById("show_asm_body").addEventListener("click", showAsmBody, false);

    document.getElementById("command_line_processor").addEventListener("change", updateDependentOptions, false);

}

function toggleTree() {
    prev_folder?.classList.remove("caret-red")
    this.parentNode.querySelector(".nested")?.classList.toggle("active");
    this.classList.toggle("caret-down");
    this.classList.add("caret-red");

    document.getElementById("selected_folder").value = this.id.replace("folder_", "");
    prev_folder = this;
}

function toggleSourceCodeLine(event) {
    const lineNumber = this.getAttribute("data-source-line");
    console.log(lineNumber);

    const targetId = `source_line_${lineNumber}`
    document.getElementById(targetId).classList.toggle("caret-red-bold");
    document.location.href = `#${targetId}`;
}

function toggleAsmBody(event) {
    this.nextSibling.classList.toggle("nested");
}

function hideAsmBody(event) {
    event.preventDefault();
    const asm = document.getElementById("compiled_code");
    if (! asm) {
        alert("No asm code is present in the browser! Run compilation first!");
        return;
    }
    const bodies = document.getElementsByClassName("asm-body");
    let i;
    for (i = 0; i < bodies.length; i++) {
        bodies[i].classList.add("nested");
    }
}

function showAsmBody(event) {
    event.preventDefault();
    const asm = document.getElementById("compiled_code");
    if (! asm) {
        alert("No asm code is present in the browser! Run compilation first!");
        return;
    }
    const bodies = document.getElementsByClassName("asm-body");
    let i;
    for (i = 0; i < bodies.length; i++) {
        bodies[i].classList.remove("nested");
    }
}

function getFile(event) {
    // if clicked then event.preventDefault and this otherwise
    event.preventDefault && event.preventDefault();
    url = this.id || event.id;

    loadFile(url);
}

function loadFile(url) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = fileOnLoad;
    xhttp.open("GET", url, true);
    xhttp.send();
}

function fileOnLoad() {
    const targetId = this.status === 200 ? "middle_place" : "code"
    document.getElementById(targetId).innerHTML = this.responseText;

    const sectionsOuter = document.getElementsByClassName("code-section-outer");
    const sectionsInner = document.getElementsByClassName("code-section-inner");

    for (i = 0; i < sectionsOuter.length; i++) {
        sectionsOuter[i].addEventListener("click", toggleSection, false);
    }
    for (i = 0; i < sectionsInner.length; i++) {
        sectionsInner[i].addEventListener("click", toggleSection, false);
    }
}

function menuDisable(event) {
    event.preventDefault();
}

function addRootFolder(event) {
    event.preventDefault();
    const url = "/folder/0/add-folder";
    return loadForm(url);
}

function addSubfolder(event) {
    event.preventDefault();
    const selectedFolder = document.getElementById("selected_folder")?.value;
    if (! selectedFolder) {
        alert("Select folder from the tree!");
        return;
    }

    const url = `/folder/${selectedFolder}/add-folder`;
    return loadForm(url);
}

function loadForm(url) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        document.getElementById("code").innerHTML = this.responseText;
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function submitAddFolder() {
    const form = document.getElementById("add_folder_form");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const {folder_id, name, parent_id} = JSON.parse(this.response);
        console.log(folder_id, name, parent_id);

        const ul = parent_id ? 
            document.getElementById(`folder_${parent_id}`).nextSibling.nextSibling : 
            document.getElementById("allFiles").getElementsByTagName("ul")[0];
        const li = document.createElement("li");
        li.innerHTML = `<span class="caret" id="folder_${folder_id}">${name}, ${folder_id}</span>
        <ul class="nested"></ul>`;
        ul.appendChild(li);

        if (parent_id) {
            ul.classList.add("active");
        }
        document.getElementById(`folder_${folder_id}`).addEventListener("click", toggleTree, false);

        form.remove();
    }
    xhttp.open(form.method, form.action, true);
    xhttp.send(new FormData(form));
}

function deleteFolder(event) {
    event.preventDefault();
    const selectedFolder = document.getElementById("selected_folder")?.value;
    if (! selectedFolder) {
        alert("Select folder from the tree!");
        return;
    }
    url = `/folder/${selectedFolder}/delete`;

    loadForm(url);
}

function submitDeleteFolder() {
    const form = document.getElementById("delete_form");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const {folder_id} = JSON.parse(this.response);

        const li = document.getElementById(`folder_${folder_id}`).parentNode;
        li.remove();

        document.getElementById("selected_folder").value = null;
        form.remove();
    }
    xhttp.open(form.method, form.action, true);
    xhttp.send(new FormData(form));
}

function addFile(event) {
    event.preventDefault();
    const selectedFolder = document.getElementById("selected_folder")?.value;
    if (! selectedFolder) {
        alert("Select folder from the tree!");
        return;
    }
    const url = `/folder/${selectedFolder}/add-file`;
    return loadForm(url);
}

function submitAddFile() {
    const form = document.getElementById("add_file_form");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const {file_id, name, folder_id} = JSON.parse(this.response);

        const ul = document.getElementById(`folder_${folder_id}`).nextSibling.nextSibling;
        const li = document.createElement("li");
        li.innerHTML = `<a href="" id="/file/${file_id}" class="file">${name}, ${file_id}</a>`;
        ul.appendChild(li);

        ul.classList.add("active");

        const elFile = document.getElementById(`/file/${file_id}`);
        elFile.addEventListener("click", getFile, false);

        form.remove();
        getFile(elFile);
    }
    xhttp.open(form.method, form.action, true);
    xhttp.send(new FormData(form));
}

function deleteFile(event) {
    event.preventDefault();
    const selectedFile = document.getElementById("selected_file")?.value;
    if (! selectedFile) {
        alert("Select file from the tree!");
        return;
    }
    const url = `/file/${selectedFile}/delete`;
    return loadForm(url);
}

function submitDeleteFile() {
    const form = document.getElementById("delete_form");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const {file_id} = JSON.parse(this.response);

        const li = document.getElementById(`/file/${file_id}`).parentNode;
        li.remove();

        form.remove();
    }
    xhttp.open(form.method, form.action, true);
    xhttp.send(new FormData(form));
}

function runSplitter(event) {
    event.preventDefault();
    const selectedFile = document.getElementById("selected_file")?.value;
    if (! selectedFile) {
        alert("Select file to be splitted!");
        return;
    }
    const url = `/file/${selectedFile}/parse`;
    loadFile(url);
}

function createSection(event) {
    event.preventDefault();
    const selectedFile = document.getElementById("selected_file")?.value;
    if (! selectedFile) {
        alert("Select file!");
        return;
    }
    const selection = document.getSelection();
    if (!(selection.toString() && selection.rangeCount)) {
        alert("Select lines!");
        return;
    }
    startLine = selection.getRangeAt(0).startContainer?.parentNode?.id?.replace("source_line_", "");
    endLine = selection.getRangeAt(0).endContainer?.parentNode?.id?.replace("source_line_", "");

    const DIRECTIVE = "directive";
    const VARIABLE = "variable";
    const PROCEDURE = "procedure";
    const COMMENT = "comment";
    const ASSEMBLY = "assembly";

    let sectionName;
    const choice = prompt(`Select section type number, one of the:\n1 - ${DIRECTIVE}\n2 - ${VARIABLE}\n3 - ${PROCEDURE}\n4 - ${COMMENT}\n5 - ${ASSEMBLY}`);
    switch(choice) {
        case "1":
            sectionName = DIRECTIVE;
            break;
        case "2":
            sectionName = VARIABLE;
            break;
        case "3":
            sectionName = PROCEDURE;
            break;
        case "4":
            sectionName = COMMENT;
            break;
        case "5":
            sectionName = ASSEMBLY;
            break;
        default:
            sectionName = null;
    }
    if (!sectionName) {
        alert("Wrong choice! No action taken.");
        return;
    }
    console.log(startLine, endLine, sectionName);
    const url = `/file/${selectedFile}/create-section/${startLine}/${endLine}/${sectionName}`

    loadFile(url);
}

function deleteSection(event) {
    event.preventDefault();
    const selectedFile = document.getElementById("selected_file")?.value;
    if (! selectedFile) {
        alert("Select file!");
        return;
    }
    const selectedSection = document.getElementById("section_to_remove").value;
    if (! selectedSection) {
        alert("Select section to be removed!");
    }
    [startLine, endLine] = selectedSection.split("-")
    console.log(startLine)
    console.log(endLine)
    console.log(selectedSection)
    const url = `/file/${selectedFile}/delete-section/${startLine.replace("start", "")}/${endLine.replace("end", "")}`
    
    loadForm(url);
}

function submitDeleteSection() {
    const form = document.getElementById("delete_form");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = fileOnLoad;
    xhttp.open(form.method, form.action, true);
    xhttp.send(new FormData(form));
}

function submitCompile(event) {
    event.preventDefault();
    const selectedFile = document.getElementById("selected_file")?.value;
    if (! selectedFile) {
        alert("Select file to be compiled!");
        return;
    }
    const cmdLineStandard = document.getElementById("command_line_standard").value;
    const cmdLineProcessor = document.getElementById("command_line_processor").value;

    if (! cmdLineStandard && ! cmdLineProcessor) {
        alert("Select STANDARD and PROCESSOR!");
        return;
    }
    if (! cmdLineStandard) {
        alert("Select STANDARD!");
        return;
    }
    if (! cmdLineProcessor) {
        alert("Select PROCESSOR!");
        return;
    }
    console.log(cmdLineStandard, cmdLineProcessor);
    document.getElementById("compiler_form_file_id").value = selectedFile;

    // document.getElementById("compiler_form").submit();

    const form = document.getElementById("compiler_form");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        fileOnLoad.bind(this)();
        fireFragmentEventListeners();
    };
    xhttp.open(form.method, form.action, true);
    xhttp.send(new FormData(form));
}

function fireFragmentEventListeners() {
    let i;
    const sourceLineRefer = document.getElementsByClassName("source-refer");
    for (i = 0; i < sourceLineRefer.length; i++) {
        sourceLineRefer[i].addEventListener("mousedown", toggleSourceCodeLine, false);
        sourceLineRefer[i].addEventListener("mouseup", toggleSourceCodeLine, false);
    }

    const asmToggler = document.getElementsByClassName("asm-header");
    for (i = 0; i < asmToggler.length; i++) {
        asmToggler[i].addEventListener("click", toggleAsmBody, false);
    }
}

function runDownloader(event) {
    event.preventDefault();
    const asm = document.getElementById("compiled_code");
    if (! asm) {
        alert("No asm code is present in the browser! Run compilation first!");
        return;
    }
    const fileName = document.getElementById("compiled_name")?.value || "compiled.asm";
    const compiledCode = getCompiledCode(asm);

    const blob = new Blob([compiledCode], {type: 'data:attachment/text;charset=utf-8;'});

    const a = document.createElement('a');
    a.href = window.URL.createObjectURL(blob);
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function getCompiledCode(asm) {
    const linesCollection = asm.getElementsByClassName("code");
    const lines = [];
    for (i = 0; i < linesCollection.length; ++i) {
        lines.push(linesCollection[i].innerText);
    }
    lines.push("");
    return lines.join("\n");
}

function updateDependentOptions() {
    dependentOptions = {
        mcs51: ['model-small', 'model-medium', 'model-large', 'model-huge'],
        ds390: ['model-flat24', 'protect-sp-update', 'stack-10bit', 'stack-probe', 'use-accelerator'],
        z80: ['no-std-crt0', 'callee-saves-bc', 'reserve-regs-iy', 'fno-omit-frame-pointer'],
        sm83: ['no-std-crt0', 'callee-saves-bc'],
        stm8: ['model-medium', 'model-large']
    };

    const processor = document.getElementById('command_line_processor').value;
    let options;

    switch (processor) {
        case 'mcs51':
            options = dependentOptions.mcs51;
            break;
        case 'ds390':
        case 'ds400':
            options = dependentOptions.ds390;
            break;
        case 'z80':
        case 'z180':
        case 'r2k':
        case 'r3ka':
        case 'tlcs90':
        case 'ez80_z80':
            options = dependentOptions.z80;
            break;
        case 'sm83':
            options = dependentOptions.sm83;
            break;
        case 'stm8':
            options = dependentOptions.stm8;
            break;
        default:
            options = null;
    };
    
    let html = '';
    options && options.forEach(option => {
        html += `<input type='checkbox' name='command_line_dependent' value='${option}' id='dependent_${option}'>
            <label for='dependent_${option}'>${option}</label><br />`;
    });
    document.getElementById('four-option').innerHTML = html;
}

function toggleSection() {
    this.classList.toggle("caret-red");
    if (this.classList.contains("caret-red")) {
        prevSection = document.getElementById("section_to_remove").value;
        if (prevSection) {
            document.getElementById(prevSection).classList.remove("caret-red");
        }
        document.getElementById("section_to_remove").value = this.id;
    }
    else {
        document.getElementById("section_to_remove").value = "";
    }
    console.log(this.id)
}

window.addEventListener("load", start, false)
