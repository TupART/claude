import os
from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def process_step2_data(df, selected_row):
    """
    Process data for Step 2 (TTG/B2E)
    """
    market = df.iloc[selected_row, 2]
    is_pcc = df.iloc[selected_row, 4] == 'Y'
    is_ds = df.iloc[selected_row, 4] == 'DS'
    windows_username = df.iloc[selected_row, 13]

    result = {}

    if is_pcc:
        result['name'] = f"{windows_username}.pcc@costa.it"
        result['users'] = f"{windows_username}@es.costa.it"

    groups = get_groups(market, is_ds)
    result['groups'] = groups

    return result

def process_step3_data(df, selected_row):
    """
    Process data for Step 3 (Genesys)
    """
    market = df.iloc[selected_row, 2]
    is_pcc = df.iloc[selected_row, 4] == 'Y'
    is_ds = df.iloc[selected_row, 4] == 'DS'
    is_tl = df.iloc[selected_row, 4] == 'TL'

    if is_ds:
        return get_digital_support_result(market)
    elif is_pcc or is_tl:
        return get_pcc_result(market)
    else:
        return get_b2c_result(market)

def get_groups(market, is_ds):
    """
    Get group assignments based on market and type
    """
    if is_ds:
        groups_map = {
            'DACH': '180, 130, 97, 160, 29',
            'Italy': '100, 160, 29',
            'Spain': '160, 29',
            'France': '110, 160, 29'
        }
    else:
        groups_map = {
            'DACH': '180, 130, 97',
            'Italy': '100',
            'Spain': '160, 29',
            'France': '110'
        }
    
    return groups_map.get(market, 'No specific groups for this market')

def get_digital_support_result(market):
    """
    Get Digital Support results for different markets
    """
    digital_support_map = {
        'Spain': {
            'division': 'UECC',
            'department': "CCH Com Ops E B2C",
            'colas': "E_CBDsManagement; E_CBDsSales; E_CBCostaClub; E_CBShorexB2C; E_Outbound; E_WAB2C; E_CBWOPT; E_CBWB2C;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, WA_CostaClub, WA_BookingSales, WA_BookingManagement, Spanish, Barcelona"
        },
        'DACH': {
            'division': 'UECC',
            'department': "CCH Com Ops DACH B2C",
            'colas': "D_WAB2C, CH_D_WAB2C, A_WAB2C, A_CBDsManagement; A_CBDsSales; A_CBCostaClub; A_Outbound; D_CBDsManagement; D_CBDsSales; D_CBCostaClub; D_Outbound; CH_D_CBDsManagement; CH_D_CBDsSales; CH_D_CBCostaClub; CH_D_Outbound; A_CBWB2C; D_CBWB2C; CH_CBWB2C; A_CBWOPT; D_CBWOPT; CH_CBWOPT; E_CBDsManagement; E_CBDsSales; E_CBCostaClub; E_CBShorexB2C; E_Outbound; E_WAB2C; E_CBWOPT; E_CBWB2C;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, WA_CostaClub, WA_BookingSales, WA_BookingManagement, German, Barcelona"
        },
        'France': {
            'division': 'UECC',
            'department': "CCH Com Ops F B2C",
            'colas': "F_CBDsManagement; F_CBDsSales; F_CBCostaClub; F_CBShorexB2C; F_Outbound; F_WAB2C; F_CBWOPT; F_CBWB2B; E_CBDsManagement; E_CBDsSales; E_CBCostaClub; E_CBShorexB2C; E_Outbound; E_WAB2C; E_CBWOPT; E_CBWB2B;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, WA_CostaClub, WA_BookingSales, WA_BookingManagement, French, Barcelona"
        },
        'Italy': {
            'division': 'UECC',
            'department': "CCH CC ITA DS",
            'colas': "I_CBDsManagement; I_CBDsSales; I_CBCostaClub; I_Outbound; I_WAB2C; I_CBWOPT; I_CBWB2C;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, WA_CostaClub, WA_BookingSales, WA_BookingManagement, Italian, Barcelona"
        }
    }
    
    return digital_support_map.get(market, {
        'division': 'UECC',
        'department': 'No specific department',
        'colas': 'No specific colas',
        'skills': 'No specific skills'
    })

def get_pcc_result(market):
    """
    Get PCC results for different markets
    """
    pcc_map = {
        'DACH': {
            'division': 'UECC',
            'department': "CCH Com Ops DACH PCC",
            'colas': "A_PCC; A_PCCDefault; A_CBWB2CPCC; A_CBWOPTPCC; A_CBFQPCC; A_CBFQPCCDefault; A_Outbound; D_PCC; D_PCCDefault; D_CBWB2CPCC; D_CBWOPTPCC; D_CBFQPCC; D_CBFQPCCDefault; D_Outbound; CH_D_PCC; CH_D_PCCDefault; CH_D_CBWB2CPCC; CH_D_CBWOPTPCC; CH_D_CBFQPCC; CH_D_CBFQPCCDefault; CH_D_Outbound; A_DsManagement; A_CBDsManagement; A_DsSales; A_CBDsSales; D_DsManagement; D_CBDsManagement; D_DsSales; D_CBDsSales; CH_D_DsManagement; CH_D_CBDsManagement; CH_D_DsSales; CH_D_CBDsSales;",
            'skills': "A_PCC:5, D_PCC:5, CH_D_PCC:5, DsSales:1, DsManagement:1, German"
        },
        'France': {
            'division': 'UECC',
            'department': "CCH Com Ops F PCC",
            'colas': "F_PCC; F_PCCDefault; F_CBWB2CPCC; F_CBWOPTPCC; F_CBFQPCC; F_CBFQPCCDefault; F_Outbound; F_DsManagement; F_CBDsManagement; F_DsSales; F_CBDsSales;",
            'skills': "F_PCC, DsSales:1, DsManagement:1, Barcelona, French"
        },
        'Spain': {
            'division': 'UECC',
            'department': "CCH Com Ops E PCC",
            'colas': "E_PCC; E_PCCDefault; E_Outbound; E_DsManagement; E_CBDsManagement; E_DsSales; E_CBDsSales;",
            'skills': "E_PCC:5, DsSales:1, DsManagement:1, Spanish"
        },
        'Italy': {
            'division': 'UECC',
            'department': "CCH CC ITA PCC",
            'colas': "I_PCC; I_PCC_Default; I_CBWB2CPCC; I_CBWOPTPCC; I_CBFQPCC; I_CBFQPCCDefault; I_Outbound;",
            'skills': "I_PCC, Barcelona, Italian"
        }
    }
    
    return pcc_map.get(market, {
        'division': 'UECC',
        'department': 'No specific department',
        'colas': 'No specific colas',
        'skills': 'No specific skills'
    })

def get_b2c_result(market):
    """
    Get B2C results for different markets
    """
    b2c_map = {
        'DACH': {
            'division': 'UECC',
            'department': "CCH Com Ops DACH B2C",
            'colas': "A_DsManagement; A_CBDsManagement; A_DsSales; A_CBDsSales; A_CostaClub; A_CBCostaClub; A_MyCosta; A_PBOR; A_Crisis; A_Outbound; D_DsManagement; D_CBDsManagement; D_DsSales; D_CBDsSales; D_CostaClub; D_CBCostaClub; D_MyCosta; D_PBOR; D_Crisis; D_Outbound; CH_D_DsManagement; CH_D_CBDsManagement; CH_D_DsSales; CH_D_CBDsSales; CH_D_CostaClub; CH_D_CBCostaClub; CH_D_MyCosta; CH_D_PBOR; D_Crisis; CH_D_Outbound",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, German"
        },
        'France': {
            'division': 'UECC',
            'department': "CCH Com Ops F B2C",
            'colas': "F_DsManagement; F_CBDsManagement; F_DsSales; F_CBDsSales; F_CostaClub; F_CBCostaClub; F_CBShorexB2C; F_PBOR; F_Crisis; F_Outbound; F_DsGRP;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, French"
        },
        'Spain': {
            'division': 'UECC',
            'department': "CCH Com Ops E B2C",
            'colas': "E_DsManagement; E_CBDsManagement; E_DsSales; E_CBDsSales; E_CostaClub; E_CBCostaClub; E_CBShorexB2C; E_PBOR; E_Crisis; E_Outbound;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, Spanish"
        },
        'Italy': {
            'division': 'UECC',
            'department': "CCH CC ITA B2C",
            'colas': "I_DsManagement; I_CBDsManagement; I_DsSales; I_CBDsSales; I_CostaClub; I_CBCostaClub; I_PBOR; I_Crisis; I_Outbound;",
            'skills': "DsSales:5, DsManagement:4, CostaClub:5, Italian"
        }
    }
    
    return b2c_map.get(market, {
        'division': 'UECC',
        'department': 'No specific department',
        'colas': 'No specific colas',
        'skills': 'No specific skills'
    })

@app.route('/')
def index():
    """
    Render the main index page
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and return row options
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    mode = request.form.get('mode', 'step2')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the file
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)

    # Read Excel file
    try:
        df = pd.read_excel(filename)
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 400

    # Prepare row options for selection
    row_options = [
        {'value': idx, 'label': f"{row[0]} - {row[1]}"} 
        for idx, row in df.iterrows() 
        if pd.notna(row[0]) and pd.notna(row[1])
    ]

    return jsonify({
        'rowOptions': row_options,
        'mode': mode,
        'filename': file.filename
    })

@app.route('/process_row', methods=['POST'])
def process_row():
    """
    Process a specific row based on selected mode
    """
    try:
        row_index = int(request.form.get('row'))
        mode = request.form.get('mode', 'step2')
        filename = request.form.get('filename')

        df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if mode == 'step2':
            result = process_step2_data(df, row_index)
        else:
            result = process_step3_data(df, row_index)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Error processing row: {str(e)}'}), 500

def validate_data_integrity(df):
    """
    Optional: Add data validation checks
    """
    required_columns = [
        'First Name', 'Last Name', 'Market', 'Type', 'Windows Username'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

def main():
    """
    Application entry point with setup checks
    """
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Optional: Add logging or additional startup checks
    print("CCH IT Spain Department Tool is starting...")
    print(f"Upload directory: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")

if __name__ == '__main__':
    app.run(debug=True)