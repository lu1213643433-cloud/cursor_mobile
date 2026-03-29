#!/usr/bin/env python3
"""
Generate an iPhone Shortcut (.shortcut) for expense tracking.
The shortcut collects expense info and appends it to a CSV file
stored in iCloud Drive / Shortcuts folder.
"""

import plistlib
import uuid as _uuid
import sys

UREPLACE = '\ufffc'

CATEGORIES = ['餐饮', '交通', '购物', '日用', '娱乐', '医疗', '教育', '其他']
FILE_PATH = 'Shortcuts/记账.csv'


def new_id():
    return str(_uuid.uuid4()).upper()


def token_str(parts):
    """Build a WFTextTokenString from a mixed list of literals and variable refs.

    Each element is one of:
      str                      → literal text
      ('var', name)            → named variable
      ('out', name, uuid_str)  → action output (magic variable)
    """
    s = ''
    att = {}
    pos = 0
    for p in parts:
        if isinstance(p, str):
            s += p
            pos += len(p)
        else:
            kind = p[0]
            s += UREPLACE
            if kind == 'var':
                att[f'{{{pos}, 1}}'] = {
                    'Type': 'Variable',
                    'VariableName': p[1],
                }
            elif kind == 'out':
                att[f'{{{pos}, 1}}'] = {
                    'Type': 'ActionOutput',
                    'OutputName': p[1],
                    'OutputUUID': p[2],
                }
            pos += 1
    if att:
        return {
            'Value': {'string': s, 'attachmentsByRange': att},
            'WFSerializationType': 'WFTextTokenString',
        }
    return s


def list_items(items):
    """Wrap plain strings into the WFArrayParameterState format."""
    return {
        'Value': [
            {
                'WFItemType': 0,
                'WFValue': {
                    'Value': {
                        'string': item,
                        'attachmentsByRange': {},
                    },
                    'WFSerializationType': 'WFTextTokenString',
                },
            }
            for item in items
        ],
        'WFSerializationType': 'WFArrayParameterState',
    }


def build_actions():
    actions = []

    # ── 1  Ask for amount ──────────────────────────────────
    ask_amount_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.ask',
        'WFWorkflowActionParameters': {
            'WFAskActionPrompt': '请输入金额',
            'WFInputType': 'Number',
            'UUID': ask_amount_id,
        },
    })
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.setvariable',
        'WFWorkflowActionParameters': {'WFVariableName': '金额'},
    })

    # ── 2  Choose category ─────────────────────────────────
    list_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.list',
        'WFWorkflowActionParameters': {
            'WFItems': list_items(CATEGORIES),
            'UUID': list_id,
        },
    })
    choose_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.choosefromlist',
        'WFWorkflowActionParameters': {
            'WFChooseFromListActionPrompt': '请选择类别',
            'UUID': choose_id,
        },
    })
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.setvariable',
        'WFWorkflowActionParameters': {'WFVariableName': '类别'},
    })

    # ── 3  Ask for note ────────────────────────────────────
    ask_note_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.ask',
        'WFWorkflowActionParameters': {
            'WFAskActionPrompt': '请输入备注（可选）',
            'WFAskActionDefaultAnswer': '',
            'WFInputType': 'Text',
            'UUID': ask_note_id,
        },
    })
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.setvariable',
        'WFWorkflowActionParameters': {'WFVariableName': '备注'},
    })

    # ── 4  Current date → formatted ───────────────────────
    date_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.date',
        'WFWorkflowActionParameters': {
            'WFDateActionMode': 'Current Date',
            'UUID': date_id,
        },
    })
    fmt_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.format.date',
        'WFWorkflowActionParameters': {
            'WFDateFormatStyle': 'Custom',
            'WFDateFormat': 'yyyy-MM-dd',
            'UUID': fmt_id,
        },
    })
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.setvariable',
        'WFWorkflowActionParameters': {'WFVariableName': '日期'},
    })

    # ── 5  Build CSV row ──────────────────────────────────
    csv_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.gettext',
        'WFWorkflowActionParameters': {
            'WFTextActionText': token_str([
                ('var', '日期'), ',',
                ('var', '金额'), ',',
                ('var', '类别'), ',',
                ('var', '备注'),
            ]),
            'UUID': csv_id,
        },
    })
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.setvariable',
        'WFWorkflowActionParameters': {'WFVariableName': '新行'},
    })

    # ── 6  Read existing CSV file from iCloud ─────────────
    get_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.documentpicker.open',
        'WFWorkflowActionParameters': {
            'WFGetFilePath': FILE_PATH,
            'WFShowFilePicker': False,
            'UUID': get_id,
        },
    })
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.setvariable',
        'WFWorkflowActionParameters': {'WFVariableName': '原内容'},
    })

    # ── 7  Combine: old content + newline + new row ───────
    combined_id = new_id()
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.gettext',
        'WFWorkflowActionParameters': {
            'WFTextActionText': token_str([
                ('var', '原内容'), '\n', ('var', '新行'),
            ]),
            'UUID': combined_id,
        },
    })

    # ── 8  Save file (overwrite) ──────────────────────────
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.documentpicker.save',
        'WFWorkflowActionParameters': {
            'WFFileDestinationPath': FILE_PATH,
            'WFSaveFileOverwrite': True,
            'WFAskWhereToSave': False,
        },
    })

    # ── 9  Show confirmation ──────────────────────────────
    actions.append({
        'WFWorkflowActionIdentifier': 'is.workflow.actions.showresult',
        'WFWorkflowActionParameters': {
            'Text': token_str([
                '✅ 记账成功！\n\n',
                '日期：', ('var', '日期'),
                '\n金额：¥', ('var', '金额'),
                '\n类别：', ('var', '类别'),
                '\n备注：', ('var', '备注'),
            ]),
        },
    })

    return actions


def build_shortcut():
    return {
        'WFWorkflowActions': build_actions(),
        'WFWorkflowClientVersion': '2302.0.4',
        'WFWorkflowHasOutputFallback': False,
        'WFWorkflowHasShortcutInputVariables': False,
        'WFWorkflowIcon': {
            'WFWorkflowIconStartColor': 4282601983,
            'WFWorkflowIconGlyphNumber': 59749,
        },
        'WFWorkflowImportQuestions': [],
        'WFWorkflowInputContentItemClasses': [
            'WFAppStoreAppContentItem',
            'WFArticleContentItem',
            'WFContactContentItem',
            'WFDateContentItem',
            'WFEmailAddressContentItem',
            'WFGenericFileContentItem',
            'WFImageContentItem',
            'WFiTunesProductContentItem',
            'WFLocationContentItem',
            'WFDCMapsLinkContentItem',
            'WFAVAssetContentItem',
            'WFPDFContentItem',
            'WFPhoneNumberContentItem',
            'WFRichTextContentItem',
            'WFSafariWebPageContentItem',
            'WFStringContentItem',
            'WFURLContentItem',
        ],
        'WFWorkflowMinimumClientVersion': 900,
        'WFWorkflowMinimumClientVersionString': '900',
        'WFWorkflowTypes': ['NCWidget', 'WatchKit'],
    }


def main():
    shortcut = build_shortcut()
    output = sys.argv[1] if len(sys.argv) > 1 else '记账助手.shortcut'
    with open(output, 'wb') as f:
        plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
    print(f'Generated: {output}')


if __name__ == '__main__':
    main()
